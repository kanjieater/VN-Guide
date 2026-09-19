import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import agent_runner
import guide_gen
import review


class ProviderTests(unittest.TestCase):
    def test_defaults_and_overrides(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(agent_runner.provider(), 'claude')
            self.assertEqual(agent_runner.model_for('GEN'), 'claude-sonnet-5')
            os.environ['GUIDE_PROVIDER'] = 'openrouter'
            self.assertEqual(agent_runner.model_for('GEN'), 'stealth/union-alpha')
            os.environ['GUIDE_MODEL'] = 'shared/model'
            os.environ['GUIDE_GEN_MODEL'] = 'role/model'
            self.assertEqual(agent_runner.model_for('GEN'), 'role/model')
            self.assertEqual(agent_runner.model_for('REVIEWER'), 'shared/model')
            os.environ['GUIDE_PROVIDER'] = 'typo'
            with self.assertRaises(ValueError):
                agent_runner.provider()

    def test_union_alpha_private_model_config(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            agent_runner._write_openrouter_model_config(tmp, 'stealth/union-alpha')
            config = json.loads((Path(tmp) / 'models.json').read_text())
            model = config['providers']['openrouter']['models'][0]
            self.assertEqual(model['id'], 'stealth/union-alpha')
            self.assertEqual(model['contextWindow'], 262144)
            self.assertEqual(model['maxTokens'], 16384)
            self.assertEqual(model['samplingParams']['max_tokens'], 16384)
            self.assertFalse(model['reasoning'])
            os.environ['GUIDE_OPENROUTER_MAX_TOKENS'] = '999999'
            with self.assertRaises(ValueError):
                agent_runner._write_openrouter_model_config(tmp, 'stealth/union-alpha')
        with tempfile.TemporaryDirectory() as tmp:
            agent_runner._write_openrouter_model_config(tmp, 'another/model')
            self.assertFalse((Path(tmp) / 'models.json').exists())

    def test_credentials_separate(self):
        with patch.dict(os.environ, {'GUIDE_PROVIDER': 'openrouter', 'ANTHROPIC_API_KEY': 'claude'}, clear=True):
            self.assertFalse(agent_runner.credentials_available())
            os.environ['OPENROUTER_API_KEY'] = 'test'
            self.assertTrue(agent_runner.credentials_available())

    def test_claude_resume_and_fresh_review(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GUIDE_PROVIDER': 'claude'}), patch('subprocess.run') as run:
            run.return_value.returncode = 0
            session = Path(tmp) / 'session.txt'
            session.write_text('claude-session-id')
            self.assertTrue(guide_gen.run_claude('task', 7, Path(tmp), session))
            self.assertIn('--resume', run.call_args.args[0])
            self.assertIn('--max-turns', run.call_args.args[0])
            self.assertTrue(review.run_claude_fresh('review'))
            self.assertNotIn('--resume', run.call_args.args[0])
            self.assertEqual(run.call_args.args[0][0], 'claude')

    def test_openrouter_ignores_claude_resume(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GUIDE_PROVIDER': 'openrouter'}), patch.object(agent_runner, 'run_openrouter', return_value=True) as run:
            session = Path(tmp) / 'session.txt'
            session.write_text('claude-session-id')
            self.assertTrue(guide_gen.run_claude('full prompt', 7, Path(tmp), session))
            self.assertEqual(run.call_args.args[0], 'full prompt')
            review.run_claude_fresh('independent review')
            self.assertEqual(run.call_args.args[0], 'independent review')

    def fake_pi(self, body, timeout=3, max_turns=3):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / 'pi'
            executable.write_text('#!' + sys.executable + '\n' + body)
            executable.chmod(0o755)
            with patch.dict(os.environ, {'PATH': tmp + ':' + os.environ['PATH'], 'OPENROUTER_API_KEY': 'fake'}):
                return agent_runner.run_openrouter('test', 'stealth/union-alpha', max_turns, root, timeout)

    def test_event_success_and_errors(self):
        self.assertTrue(self.fake_pi('print(\'{"type":"message_end","message":{"role":"assistant","stopReason":"stop"}}\')\nprint(\'{"type":"agent_end"}\')'))
        self.assertFalse(self.fake_pi('print(\'{"type":"agent_end"}\')'))
        self.assertFalse(self.fake_pi('print(\'{"type":"message_end","message":{"role":"assistant","stopReason":"error"}}\')\nprint(\'{"type":"agent_end"}\')'))
        self.assertFalse(self.fake_pi('print("no completion")'))
        self.assertFalse(self.fake_pi('import sys\nprint(\'{"type":"agent_end"}\')\nsys.exit(1)'))

    def test_recovered_provider_error(self):
        self.assertTrue(self.fake_pi('print(\'{"type":"message_end","message":{"role":"assistant","stopReason":"error"}}\')\nprint(\'{"type":"message_end","message":{"role":"assistant","stopReason":"stop"}}\')\nprint(\'{"type":"agent_end"}\')'))

    def test_terminal_completion_required(self):
        for reason in ['length', 'toolUse', 'error', 'aborted', None]:
            event = json.dumps({'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': reason}})
            with self.subTest(reason=reason):
                self.assertFalse(self.fake_pi('print(' + repr(event) + ')\nprint(\'{"type":"agent_end"}\')'))
        self.assertFalse(self.fake_pi('print(\'{"type":"auto_retry_end","success":true}\')\nprint(\'{"type":"agent_end"}\')'))
        self.assertTrue(self.fake_pi('print(\'{"type":"message_end","message":{"role":"assistant","stopReason":"length"}}\')\nprint(\'{"type":"turn_start"}\')\nprint(\'{"type":"message_end","message":{"role":"assistant","stopReason":"stop"}}\')\nprint(\'{"type":"agent_end"}\')'))

    def test_driver_sigterm_reaps_pi(self):
        import signal
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake = root / 'pi'
            fake.write_text('#!' + sys.executable + '\nimport os,time\nfrom pathlib import Path\nPath("pi.pid").write_text(str(os.getpid()))\nprint("ready",flush=True)\ntime.sleep(60)\nPath("late-write").touch()\n')
            fake.chmod(0o755)
            script_dir = str(Path(agent_runner.__file__).parent)
            driver = f'import sys; sys.path.insert(0,{script_dir!r}); import agent_runner; from pathlib import Path; agent_runner.run_openrouter("test","stealth/union-alpha",3,Path({tmp!r}),90)'
            env = dict(os.environ, OPENROUTER_API_KEY='fake', PATH=tmp + ':' + os.environ['PATH'])
            proc = subprocess.Popen([sys.executable, '-c', driver], env=env, stdout=subprocess.PIPE, text=True)
            try:
                while proc.stdout.readline().strip() != 'ready':
                    if proc.poll() is not None:
                        self.fail('driver exited before fake Pi started')
                pid = int((root / 'pi.pid').read_text())
                proc.send_signal(signal.SIGTERM)
                self.assertEqual(proc.wait(timeout=10), 143)
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)
                self.assertFalse((root / 'late-write').exists())
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                proc.stdout.close()

    def test_turn_limit(self):
        self.assertFalse(self.fake_pi('print(\'{"type":"turn_start"}\')\nprint(\'{"type":"turn_start"}\')\nprint(\'{"type":"agent_end"}\')', max_turns=1))

    def test_timeout_allows_detached_tool_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / 'late-write'
            body = f'''import subprocess,signal,os,time
child = subprocess.Popen(['bash','-c', 'sleep 1; touch {sentinel}'], start_new_session=True)
def stop(*args):
    os.killpg(child.pid, signal.SIGKILL)
    child.wait()
    raise SystemExit(1)
signal.signal(signal.SIGTERM, stop)
time.sleep(10)
'''
            self.assertFalse(self.fake_pi(body, timeout=0.3))
            time.sleep(1.1)  # Regression assertion, not job polling.
            self.assertFalse(sentinel.exists())

    def test_priority_does_not_chain_games(self):
        with tempfile.TemporaryDirectory() as tmp:
            games = Path(tmp) / 'games.json'
            games.write_text(json.dumps({'v210': {'slug': 'himawari'}, 'v999': {'slug': 'other'}}))
            with patch.dict(os.environ, {'GUIDE_PRIORITY_VID': 'v210'}), patch.object(agent_runner, 'credentials_available', return_value=True), patch.object(guide_gen, 'GAMES_JSON', games), patch.object(guide_gen, 'generate_guide', return_value=True) as generate, patch.object(guide_gen, 'run_deploy'), patch.object(guide_gen._generate, 'generate_landing'):
                guide_gen.run()
                self.assertEqual(generate.call_count, 1)
                self.assertEqual(generate.call_args.args[0], 'himawari')


class ReviewTests(unittest.TestCase):
    def test_approval_cannot_modify_other_metadata(self):
        snapshot = {'title': 'Game', 'routes': [{'id': 'r1', 'reviewed': False}, {'id': 'r2', 'reviewed': False}]}
        valid = json.loads(json.dumps(snapshot))
        valid['routes'][0]['reviewed'] = True
        bad_outputs = [
            {'routes': [valid['routes'][0]]},
            dict(valid, routes=list(reversed(valid['routes']))),
            dict(valid, title='Changed'),
            dict(valid, routes=[valid['routes'][0], {'id': 'r2', 'reviewed': True}]),
            dict(valid, routes=[{'id': 'r1', 'reviewed': 1}, valid['routes'][1]]),
        ]
        for output in [valid] + bad_outputs:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'guide.json'
                original = json.dumps(snapshot)
                path.write_text(original)
                def approve(*args):
                    path.write_text(json.dumps(output))
                    return True
                with patch.object(review, '_mark_route_reviewed', side_effect=approve):
                    accepted = review.mark_route_reviewed(path, 'game', 'r1', 'R1')
                self.assertEqual(accepted, output is valid)
                if not accepted:
                    self.assertEqual(path.read_text(), original)

    def test_issue_lookup_fails_closed(self):
        for function in [review.get_open_issue_for_route, review.get_open_structural_issue_for_route]:
            for code, output in [(1, ''), (0, 'broken'), (0, '{}'), (0, '')]:
                with patch('subprocess.run', return_value=subprocess.CompletedProcess([], code, output, 'failure')):
                    with self.assertRaises((RuntimeError, ValueError)):
                        function('game', 'route')

    def test_rewrite_loop_uses_separate_calls(self):
        for loop, lookup in [(review.structural_review_route, 'get_open_structural_issue_for_route'), (review.review_route, 'get_open_issue_for_route')]:
            with patch.object(review, lookup, side_effect=[None, 42, None]), patch.object(review, 'run_claude_fresh', return_value=True) as run, patch.object(review, 'run_deploy'):
                self.assertTrue(loop('game', 'route', 'Route'))
                self.assertEqual(run.call_count, 3)
                prompts = [call.args[0] for call in run.call_args_list]
                self.assertIn('reviewer', prompts[0])
                self.assertIn('guide-author.md', prompts[1])
                self.assertIn('Do NOT close', prompts[1])
                self.assertIn('Re-review', prompts[2])

    def test_structural_failure_prevents_accuracy(self):
        with tempfile.TemporaryDirectory() as tmp:
            guide = Path(tmp) / 'game' / 'guide.json'
            guide.parent.mkdir()
            guide.write_text('{"routes":[{"id":"route","reviewed":false}]}')
            with patch.object(review, 'REPO_PATH', Path(tmp)), patch.object(review, 'structural_review_route', return_value=False), patch.object(review, 'review_route') as accuracy:
                review.review_game('game')
                accuracy.assert_not_called()

    def test_approval_exception_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            guide = Path(tmp) / 'game' / 'guide.json'
            guide.parent.mkdir()
            guide.write_text('{"routes":[{"id":"route","reviewed":false}]}')

            def approve(*args, **kwargs):
                guide.write_text('{"routes":[{"id":"route","reviewed":true}]}')
                return True

            with patch.object(review, 'REPO_PATH', Path(tmp)), patch.object(review, 'structural_review_route', return_value=True), patch.object(review, 'review_route', return_value=True), patch.object(review, 'run_claude_fresh', side_effect=approve), patch.object(review, 'get_open_issue_for_route', side_effect=[None, RuntimeError('GitHub offline')]), patch.object(review, 'get_open_structural_issue_for_route', return_value=None):
                with self.assertRaises(RuntimeError):
                    review.review_game('game')
                self.assertFalse(json.loads(guide.read_text())['routes'][0]['reviewed'])

    def test_approval_rollback_restores_malformed_metadata(self):
        malformed = [
            '{"routes":[null,{"id":"route","reviewed":true}]}',
            '{"routes":[{"reviewed":true}],"id":"route"}',
            '{"routes":{"id":"route","reviewed":true}}',
            '{"routes":[{"id":"other","reviewed":true}]}',
        ]
        snapshot = '{"routes":[{"id":"route","reviewed":false}]}'
        for broken in malformed:
            with self.subTest(broken=broken):
                with tempfile.TemporaryDirectory() as tmp:
                    guide = Path(tmp) / 'game' / 'guide.json'
                    guide.parent.mkdir()
                    guide.write_text(snapshot)

                    def approve(*args, **kwargs):
                        guide.write_text(broken)
                        return True

                    with patch.object(review, 'REPO_PATH', Path(tmp)), patch.object(review, 'structural_review_route', return_value=True), patch.object(review, 'review_route', return_value=True), patch.object(review, 'run_claude_fresh', side_effect=approve), patch.object(review, 'get_open_issue_for_route', side_effect=[None, RuntimeError('GitHub offline')]), patch.object(review, 'get_open_structural_issue_for_route', return_value=None):
                        with self.assertRaises(RuntimeError):
                            review.review_game('game')
                    restored = json.loads(guide.read_text())
                    self.assertEqual(restored, json.loads(snapshot))


if __name__ == '__main__':
    unittest.main()

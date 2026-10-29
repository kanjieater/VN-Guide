// Read-only verifier using AuroraWright/knife's original asset parsers.
// Only the requested choice strings and their SELR references are printed.
use knife_core::format::script::{SceneArchive, ScriptText};
use knife_core::vm::parse::Scene;
use std::{collections::BTreeSet, env, fs, path::PathBuf};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = PathBuf::from(env::args().nth(1).expect("supply the extracted romfs directory"));
    let ids = [42688, 42607, 42639, 42694, 42695, 42725, 42724, 42734, 42735, 42750, 42751, 42754, 42755];
    let strings = ScriptText::parse(&fs::read(root.join("script_text.mrg"))?, 0)?;
    let scenes = SceneArchive::parse(&fs::read(root.join("allscr.mrg"))?)?;
    let mut referenced = BTreeSet::new();
    for id in ids {
        println!("TEXT\t{id}\t{}", strings.get(id).expect("missing choice string"));
    }
    for scene_index in 0..scenes.scene_count() {
        let scene = Scene::parse(scenes.scene(scene_index).expect("missing scene"));
        for command in &scene.commands {
            if !command.is("SELR") { continue; }
            for id in ids {
                let reference = format!("${id:06}");
                if command.args.iter().any(|arg| arg.contains(&reference)) {
                    referenced.insert(id);
                    let name = scenes.names.get(scene_index).map(String::as_str).unwrap_or("<unnamed>");
                    println!("SELR\t{id}\t{name}\t0x{:x}\t{}", command.offset, command.args.join(","));
                }
            }
        }
    }
    assert_eq!(referenced.len(), ids.len(), "not every extracted string is referenced by SELR");
    println!("VERIFIED\t{}\tchoice strings referenced by scene SELR instructions", ids.len());
    Ok(())
}

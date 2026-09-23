(() => {
const root = document.documentElement;
const savedSort = localStorage.getItem("vn-guide-sort");
const savedFilter = localStorage.getItem("vn-guide-filter");
root.dataset.vngSort = savedSort === "alpha" ? "alpha" : "recent";
root.dataset.vngFilter = savedFilter === "playing" ? "playing" : "all";
})();

const icons = {
  upload: '<svg viewBox="0 0 24 24"><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M20 16v4H4v-4"/></svg>',
  copy: '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
  edit: '<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  star: '<svg viewBox="0 0 24 24"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2 7.5 14 3 9.6l6.2-.9Z"/></svg>',
  grid: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
  list: '<svg viewBox="0 0 24 24"><path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/></svg>',
  plus: '<svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M5 12h14"/></svg>',
  close: '<svg viewBox="0 0 24 24"><path d="m18 6-12 12"/><path d="m6 6 12 12"/></svg>',
  trash: '<svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 15H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>',
  download: '<svg viewBox="0 0 24 24"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
  share: '<svg viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4"/><path d="m15.4 6.5-6.8 4"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="m20 6-11 11-5-5"/></svg>',
  monitor: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8"/><path d="M12 16v4"/></svg>',
  sun: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
  moon: '<svg viewBox="0 0 24 24"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z"/></svg>'
};

const state = {
  activeCategory: "Alle",
  activeMode: "all",
  query: "",
  view: "grid",
  categories: [],
  images: [],
  pendingFiles: [],
  editing: null,
  selected: new Set()
};

const grid = document.querySelector("#grid");
const filters = document.querySelector("#filters");
const categoriesNav = document.querySelector("#categories");
const count = document.querySelector("#count");
const empty = document.querySelector("#empty");
const search = document.querySelector("#search");
const categoryList = document.querySelector("#category-list");
const uploadCategoryCombo = document.querySelector("#upload-category-combo");
const uploadCategoryToggle = document.querySelector("#upload-category-toggle");
const uploadOpen = document.querySelector("#upload-open");
const uploadDialog = document.querySelector("#upload-dialog");
const uploadForm = document.querySelector("#upload-form");
const uploadFiles = document.querySelector("#upload-files");
const uploadCategory = document.querySelector("#upload-category");
const uploadStatus = document.querySelector("#upload-status");
const dropzone = document.querySelector("#dropzone");
const selectedFiles = document.querySelector("#selected-files");
const categoryForm = document.querySelector("#category-form");
const categoryStatus = document.querySelector("#category-status");
const editDialog = document.querySelector("#edit-dialog");
const editForm = document.querySelector("#edit-form");
const editName = document.querySelector("#edit-name");
const editCategory = document.querySelector("#edit-category");
const editStatus = document.querySelector("#edit-status");
const deleteImage = document.querySelector("#delete-image");
const viewGrid = document.querySelector("#view-grid");
const viewList = document.querySelector("#view-list");
const dropOverlay = document.querySelector("#drop-overlay");
const uploadCancel = document.querySelector("#upload-cancel");
const previewDialog = document.querySelector("#preview-dialog");
const previewTitle = document.querySelector("#preview-title");
const previewImage = document.querySelector("#preview-image");
const previewAddress = document.querySelector("#preview-address");
const previewCopy = document.querySelector("#preview-copy");
const bulkActions = document.querySelector("#bulk-actions");
const selectionClear = document.querySelector("#selection-clear");
const bulkDelete = document.querySelector("#bulk-delete");
const bulkDownload = document.querySelector("#bulk-download");
const bulkShare = document.querySelector("#bulk-share");
const categoryDialog = document.querySelector("#category-dialog");
const categoryEditForm = document.querySelector("#category-edit-form");
const categoryEditName = document.querySelector("#category-edit-name");
const categoryEditStatus = document.querySelector("#category-edit-status");
const categoryEditDelete = document.querySelector("#category-edit-delete");
const themeToggle = document.querySelector("#theme-toggle");
const diskPill = document.querySelector("#disk-pill");
const confirmDialog = document.querySelector("#confirm-dialog");
const confirmTitle = document.querySelector("#confirm-title");
const confirmMessage = document.querySelector("#confirm-message");
const confirmCancel = document.querySelector("#confirm-cancel");
const confirmOk = document.querySelector("#confirm-ok");

uploadOpen.innerHTML = icons.upload;
themeToggle.innerHTML = icons.monitor;
viewGrid.innerHTML = icons.grid;
viewList.innerHTML = icons.list;
document.querySelector("#upload-large-icon").innerHTML = icons.upload;
document.querySelectorAll('button[value="cancel"]').forEach((button) => { button.innerHTML = icons.close; });
categoryForm.querySelector("button").innerHTML = icons.plus;
previewCopy.innerHTML = icons.copy;
selectionClear.innerHTML = icons.close;
bulkDelete.innerHTML = icons.trash;
bulkDownload.innerHTML = icons.download;
bulkShare.innerHTML = icons.share;

let editingCategory = "";
let themeMode = localStorage.getItem("picshelf-theme") || "system";
let confirmResolve = null;

function applyTheme() {
  document.documentElement.dataset.theme = themeMode === "system" ? "" : themeMode;
  if (themeMode === "light") {
    themeToggle.innerHTML = icons.sun;
    themeToggle.title = "Theme: Hell";
    themeToggle.setAttribute("aria-label", "Theme: Hell");
  } else if (themeMode === "dark") {
    themeToggle.innerHTML = icons.moon;
    themeToggle.title = "Theme: Dunkel";
    themeToggle.setAttribute("aria-label", "Theme: Dunkel");
  } else {
    themeToggle.innerHTML = icons.monitor;
    themeToggle.title = "Theme: System";
    themeToggle.setAttribute("aria-label", "Theme: System");
  }
}

function cycleTheme() {
  themeMode = themeMode === "system" ? "light" : themeMode === "light" ? "dark" : "system";
  localStorage.setItem("picshelf-theme", themeMode);
  applyTheme();
}

applyTheme();

function absoluteUrl(url) {
  return new URL(url, window.location.href).href;
}

function formatCount(value) {
  return value === 1 ? "1 Bild" : `${value} Bilder`;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let value = bytes / 1024;
  let unit = units.shift();
  while (value >= 1024 && units.length) {
    value /= 1024;
    unit = units.shift();
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${unit}`;
}

function renderDisk(disk) {
  if (!disk) {
    diskPill.replaceChildren();
    return;
  }
  diskPill.title = `${formatBytes(disk.free)} frei von ${formatBytes(disk.total)}`;
  diskPill.innerHTML = `
    <div class="disk-text">${formatBytes(disk.free)} frei</div>
    <div class="disk-bar"><div class="disk-fill" style="--disk-used: ${disk.percentUsed}%"></div></div>
  `;
}

function askConfirm({ title = "Bestätigen", message, action = "Löschen" }) {
  confirmTitle.textContent = title;
  confirmMessage.textContent = message;
  confirmOk.textContent = action;
  confirmDialog.showModal();
  return new Promise((resolve) => {
    confirmResolve = resolve;
  });
}

function resolveConfirm(value) {
  if (confirmResolve) {
    confirmResolve(value);
    confirmResolve = null;
  }
  if (confirmDialog.open) confirmDialog.close();
}

function closeOnBackdrop(dialog, onClose = () => dialog.close()) {
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    const clickedBackdrop = event.clientX < bounds.left
      || event.clientX > bounds.right
      || event.clientY < bounds.top
      || event.clientY > bounds.bottom;
    if (clickedBackdrop) onClose();
  });
}

closeOnBackdrop(uploadDialog);
closeOnBackdrop(editDialog);
closeOnBackdrop(categoryDialog);
closeOnBackdrop(previewDialog);
closeOnBackdrop(confirmDialog, () => resolveConfirm(false));

function categoryNames() {
  return state.categories.map((category) => category.name);
}

function editableCategoryNames() {
  return ["Allgemein", ...categoryNames().filter((name) => name !== "Allgemein")];
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.className = isError ? "status error" : "status";
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Accept": "application/json",
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

function visibleImages() {
  const query = state.query.trim().toLowerCase();
  return state.images.filter((image) => {
    const modeMatches = state.activeMode === "all"
      || (state.activeMode === "favorites" && image.favorite)
      || (state.activeMode === "category" && image.category === state.activeCategory);
    const queryMatches = !query
      || image.name.toLowerCase().includes(query)
      || image.fileName.toLowerCase().includes(query)
      || image.category.toLowerCase().includes(query);
    return modeMatches && queryMatches;
  });
}

function selectedImages() {
  return state.images.filter((image) => state.selected.has(image.path));
}

function selectedPaths() {
  return selectedImages().map((image) => image.path);
}

function navButton(label, countValue, mode, category = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "nav-item";
  if (state.activeMode === mode && (mode !== "category" || state.activeCategory === category)) {
    button.classList.add("active");
  }
  const text = document.createElement("span");
  text.textContent = label;
  const badge = document.createElement("span");
  badge.className = "badge";
  badge.textContent = countValue;
  button.append(text, badge);
  if (mode === "category" && category !== "Allgemein") {
    const edit = document.createElement("span");
    edit.className = "nav-edit";
    edit.title = "Kategorie bearbeiten";
    edit.setAttribute("aria-label", "Kategorie bearbeiten");
    edit.innerHTML = icons.edit;
    edit.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      openCategoryDialog(category);
    });
    button.append(edit);
  }
  button.addEventListener("click", () => {
    state.activeMode = mode;
    state.activeCategory = category;
    render();
  });
  return button;
}

function renderFilters() {
  const favoriteCount = state.images.filter((image) => image.favorite).length;
  filters.replaceChildren(
    navButton("Alle Bilder", state.images.length, "all"),
    navButton("Favoriten", favoriteCount, "favorites")
  );
  categoriesNav.replaceChildren(...state.categories.map((category) =>
    navButton(category.name, category.items.length, "category", category.name)
  ));
  renderCategoryMenu();
  editCategory.replaceChildren(...editableCategoryNames().map((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    return option;
  }));
}

function renderCategoryMenu() {
  const query = uploadCategory.value.trim().toLowerCase();
  const names = categoryNames().filter((name) => !query || name.toLowerCase().includes(query));
  if (!names.length) {
    const empty = document.createElement("div");
    empty.className = "combo-empty";
    empty.textContent = query ? "Neue Kategorie wird angelegt" : "Keine Kategorien";
    categoryList.replaceChildren(empty);
    return;
  }
  categoryList.replaceChildren(...names.map((name) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "combo-option";
    if (uploadCategory.value === name) option.classList.add("active");
    option.role = "option";
    option.textContent = name;
    option.addEventListener("click", () => {
      uploadCategory.value = name;
      closeCategoryMenu();
    });
    return option;
  }));
}

function openCategoryMenu() {
  renderCategoryMenu();
  uploadCategoryCombo.classList.add("open");
}

function closeCategoryMenu() {
  uploadCategoryCombo.classList.remove("open");
}

function openCategoryDialog(category) {
  editingCategory = category;
  categoryEditName.value = category;
  setStatus(categoryEditStatus, "");
  categoryDialog.showModal();
}

async function copyAddress(button, image) {
  const value = absoluteUrl(image.url);
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const input = document.createElement("input");
    input.value = value;
    document.body.append(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  }
  button.classList.add("active");
  window.setTimeout(() => button.classList.remove("active"), 900);
}

function iconButton(icon, label, className = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `icon-button ${className}`.trim();
  button.title = label;
  button.setAttribute("aria-label", label);
  button.innerHTML = icons[icon];
  return button;
}

function imageCard(image) {
  const card = document.createElement("article");
  card.className = "card";
  if (state.selected.has(image.path)) card.classList.add("selected");

  const selectWrap = document.createElement("label");
  selectWrap.className = "select-wrap";
  selectWrap.title = "Auswählen";
  const selector = document.createElement("input");
  selector.type = "checkbox";
  selector.checked = state.selected.has(image.path);
  selector.setAttribute("aria-label", `${image.fileName} auswählen`);
  selector.addEventListener("change", () => {
    if (selector.checked) {
      state.selected.add(image.path);
    } else {
      state.selected.delete(image.path);
    }
    render();
  });
  selectWrap.append(selector);

  const preview = document.createElement("a");
  preview.className = "preview";
  preview.href = image.url;
  preview.addEventListener("click", (event) => {
    event.preventDefault();
    openPreview(image);
  });

  const img = document.createElement("img");
  img.src = image.url;
  img.alt = image.name;
  img.loading = "lazy";
  preview.append(img);

  const meta = document.createElement("div");
  meta.className = "meta";

  const top = document.createElement("div");
  top.className = "card-top";
  const titleWrap = document.createElement("div");
  const name = document.createElement("p");
  name.className = "name";
  name.textContent = image.fileName;
  const category = document.createElement("div");
  category.className = "category";
  category.textContent = image.category;
  const details = document.createElement("div");
  details.className = "image-details";
  details.innerHTML = `<span>${formatBytes(image.size)}</span><span>${image.path}</span>`;
  titleWrap.append(name, category, details);
  top.append(titleWrap);

  const actions = document.createElement("div");
  actions.className = "card-actions";
  const favorite = iconButton("star", image.favorite ? "Favorit entfernen" : "Favorit", "favorite");
  if (image.favorite) favorite.classList.add("active");
  favorite.addEventListener("click", () => runCardAction(card, async () => {
    await apiJson("/api/images/favorite", {
      method: "POST",
      body: JSON.stringify({ path: image.path, favorite: !image.favorite })
    });
  }));
  const copy = iconButton("copy", "Adresse kopieren");
  copy.addEventListener("click", () => copyAddress(copy, image));
  const edit = iconButton("edit", "Bearbeiten");
  edit.addEventListener("click", () => openEdit(image));
  actions.append(favorite, copy, edit);

  meta.append(top, actions);
  card.append(selectWrap, preview, meta);
  return card;
}

function openPreview(image) {
  previewTitle.textContent = image.fileName;
  previewImage.src = image.url;
  previewImage.alt = image.name;
  previewAddress.value = absoluteUrl(image.url);
  previewCopy.onclick = () => copyAddress(previewCopy, image);
  previewDialog.showModal();
}

async function runCardAction(card, action) {
  const buttons = card.querySelectorAll("button");
  buttons.forEach((button) => { button.disabled = true; });
  try {
    await action();
    await load();
  } catch (error) {
    window.alert(error.message || "Aktion fehlgeschlagen.");
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
  }
}

function render() {
  renderFilters();
  const images = visibleImages();
  grid.className = state.view === "list" ? "grid list" : "grid";
  grid.replaceChildren(...images.map(imageCard));
  const selectedCount = state.selected.size;
  count.textContent = selectedCount ? `${formatCount(images.length)} · ${selectedCount} ausgewählt` : formatCount(images.length);
  empty.style.display = images.length ? "none" : "block";
  viewGrid.classList.toggle("active", state.view === "grid");
  viewList.classList.toggle("active", state.view === "list");
  bulkActions.hidden = selectedCount === 0;
}

async function load() {
  try {
    const data = await apiJson("/api/images");
    state.categories = data.categories;
    state.images = data.categories.flatMap((category) => category.items);
    renderDisk(data.disk);
    const existingPaths = new Set(state.images.map((image) => image.path));
    state.selected = new Set([...state.selected].filter((path) => existingPaths.has(path)));
    if (state.activeMode === "category" && !categoryNames().includes(state.activeCategory)) {
      state.activeMode = "all";
      state.activeCategory = "Alle";
    }
    render();
  } catch (error) {
    count.innerHTML = '<span class="error">Fehler beim Laden</span>';
    empty.textContent = "Die Galerie konnte nicht geladen werden.";
    empty.style.display = "block";
    console.error(error);
  }
}

function setPendingFiles(files) {
  state.pendingFiles = [...files].filter((file) => file.type.startsWith("image/") || file.name.toLowerCase().endsWith(".svg"));
  selectedFiles.textContent = state.pendingFiles.length
    ? `${state.pendingFiles.length} ausgewählt`
    : "Bild ablegen oder auswählen";
}

function openUpload(files = []) {
  setPendingFiles(files);
  setStatus(uploadStatus, "");
  if (!uploadDialog.open) uploadDialog.showModal();
}

function openEdit(image) {
  state.editing = image;
  editName.value = image.fileName;
  editCategory.value = image.category;
  setStatus(editStatus, "");
  editDialog.showModal();
}

search.addEventListener("input", () => {
  state.query = search.value;
  render();
});

themeToggle.addEventListener("click", cycleTheme);
confirmCancel.addEventListener("click", () => resolveConfirm(false));
confirmOk.addEventListener("click", () => resolveConfirm(true));
confirmDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  resolveConfirm(false);
});
confirmDialog.addEventListener("close", () => {
  if (confirmResolve) resolveConfirm(false);
});

viewGrid.addEventListener("click", () => {
  state.view = "grid";
  render();
});

viewList.addEventListener("click", () => {
  state.view = "list";
  render();
});

uploadOpen.addEventListener("click", () => openUpload());
uploadCancel.addEventListener("click", () => uploadDialog.close());
dropzone.addEventListener("click", () => uploadFiles.click());
uploadFiles.addEventListener("change", () => setPendingFiles(uploadFiles.files));
uploadCategory.addEventListener("focus", openCategoryMenu);
uploadCategory.addEventListener("input", openCategoryMenu);
uploadCategoryToggle.addEventListener("click", () => {
  if (uploadCategoryCombo.classList.contains("open")) {
    closeCategoryMenu();
  } else {
    uploadCategory.focus();
    openCategoryMenu();
  }
});
document.addEventListener("click", (event) => {
  if (!uploadCategoryCombo.contains(event.target)) closeCategoryMenu();
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragging");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragging"));
dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  event.stopPropagation();
  dropzone.classList.remove("dragging");
  openUpload(event.dataTransfer.files);
});

let dragDepth = 0;
window.addEventListener("dragenter", (event) => {
  if (![...event.dataTransfer.types].includes("Files")) return;
  dragDepth += 1;
  dropOverlay.classList.add("visible");
});
window.addEventListener("dragleave", () => {
  dragDepth = Math.max(0, dragDepth - 1);
  if (dragDepth === 0) dropOverlay.classList.remove("visible");
});
window.addEventListener("dragover", (event) => {
  if ([...event.dataTransfer.types].includes("Files")) event.preventDefault();
});
window.addEventListener("drop", (event) => {
  if (![...event.dataTransfer.types].includes("Files")) return;
  event.preventDefault();
  dragDepth = 0;
  dropOverlay.classList.remove("visible");
  openUpload(event.dataTransfer.files);
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.pendingFiles.length) {
    setStatus(uploadStatus, "Keine Bilddatei ausgewählt.", true);
    return;
  }
  const formData = new FormData();
  for (const file of state.pendingFiles) formData.append("files", file, file.name);
  formData.append("category", uploadCategory.value);
  setStatus(uploadStatus, "Import läuft");
  try {
    await apiJson("/api/upload", { method: "POST", body: formData });
    uploadForm.reset();
    setPendingFiles([]);
    uploadDialog.close();
    await load();
  } catch (error) {
    setStatus(uploadStatus, error.message || "Upload fehlgeschlagen.", true);
  }
});

categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.querySelector("#new-category");
  setStatus(categoryStatus, "");
  try {
    const data = await apiJson("/api/categories", {
      method: "POST",
      body: JSON.stringify({ name: input.value })
    });
    input.value = "";
    state.activeMode = "category";
    state.activeCategory = data.category;
    await load();
  } catch (error) {
    setStatus(categoryStatus, error.message || "Kategorie konnte nicht angelegt werden.", true);
  }
});

categoryEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!editingCategory) return;
  setStatus(categoryEditStatus, "Speichere");
  try {
    const data = await apiJson("/api/categories/rename", {
      method: "POST",
      body: JSON.stringify({ name: editingCategory, newName: categoryEditName.value })
    });
    state.activeMode = "category";
    state.activeCategory = data.category;
    categoryDialog.close();
    await load();
  } catch (error) {
    setStatus(categoryEditStatus, error.message || "Kategorie konnte nicht umbenannt werden.", true);
  }
});

categoryEditDelete.addEventListener("click", async () => {
  if (!editingCategory) return;
  const category = editingCategory;
  const imageCount = state.categories.find((item) => item.name === category)?.items.length || 0;
  const message = imageCount
    ? `Kategorie ${category} mit ${imageCount} Bildern wirklich löschen?`
    : `Kategorie ${category} wirklich löschen?`;
  categoryDialog.close();
  const confirmed = await askConfirm({
    title: "Kategorie löschen",
    message,
    action: "Löschen"
  });
  if (!confirmed) {
    openCategoryDialog(category);
    return;
  }
  setStatus(categoryEditStatus, "Lösche");
  try {
    await apiJson("/api/categories/delete", {
      method: "POST",
      body: JSON.stringify({ name: category })
    });
    state.activeMode = "all";
    state.activeCategory = "Alle";
    state.selected.clear();
    categoryDialog.close();
    await load();
  } catch (error) {
    setStatus(categoryEditStatus, error.message || "Kategorie konnte nicht gelöscht werden.", true);
  }
});

selectionClear.addEventListener("click", () => {
  state.selected.clear();
  render();
});

bulkDelete.addEventListener("click", async () => {
  const paths = selectedPaths();
  if (!paths.length) return;
  const confirmed = await askConfirm({
    title: "Bilder löschen",
    message: `${paths.length} ausgewählte Bilder wirklich löschen?`,
    action: "Löschen"
  });
  if (!confirmed) return;
  try {
    await apiJson("/api/images/delete-bulk", {
      method: "POST",
      body: JSON.stringify({ paths })
    });
    state.selected.clear();
    await load();
  } catch (error) {
    window.alert(error.message || "Löschen fehlgeschlagen.");
  }
});

bulkDownload.addEventListener("click", async () => {
  const paths = selectedPaths();
  if (!paths.length) return;
  try {
    const response = await fetch("/api/images/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths })
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || `HTTP ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "picshelf-images.zip";
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    window.alert(error.message || "Download fehlgeschlagen.");
  }
});

bulkShare.addEventListener("click", async () => {
  const images = selectedImages();
  if (!images.length) return;
  const links = images.map((image) => absoluteUrl(image.url));
  const text = links.join("\n");
  try {
    if (navigator.share) {
      await navigator.share({ title: "PicShelf", text });
    } else {
      await navigator.clipboard.writeText(text);
      window.alert("Adressen wurden kopiert.");
    }
  } catch (error) {
    if (error.name !== "AbortError") {
      await navigator.clipboard.writeText(text);
      window.alert("Adressen wurden kopiert.");
    }
  }
});

editForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.editing) return;
  setStatus(editStatus, "Speichere");
  try {
    const original = state.editing;
    let currentPath = original.path;
    if (editName.value !== original.fileName) {
      const renamed = await apiJson("/api/images/rename", {
        method: "POST",
        body: JSON.stringify({ path: currentPath, newName: editName.value })
      });
      currentPath = renamed.path;
    }
    if (editCategory.value !== original.category) {
      await apiJson("/api/images/move", {
        method: "POST",
        body: JSON.stringify({ path: currentPath, category: editCategory.value })
      });
    }
    editDialog.close();
    await load();
  } catch (error) {
    setStatus(editStatus, error.message || "Speichern fehlgeschlagen.", true);
  }
});

deleteImage.addEventListener("click", async () => {
  if (!state.editing) return;
  const editingImage = state.editing;
  editDialog.close();
  const confirmed = await askConfirm({
    title: "Bild löschen",
    message: `${editingImage.fileName} wirklich löschen?`,
    action: "Löschen"
  });
  if (!confirmed) {
    openEdit(editingImage);
    return;
  }
  setStatus(editStatus, "Lösche");
  try {
    await apiJson("/api/images/delete", {
      method: "POST",
      body: JSON.stringify({ path: editingImage.path })
    });
    editDialog.close();
    await load();
  } catch (error) {
    setStatus(editStatus, error.message || "Löschen fehlgeschlagen.", true);
  }
});

load();

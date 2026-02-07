const apiBaseInput = document.getElementById("apiBase");
const saveApiBaseBtn = document.getElementById("saveApiBase");

const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");
const toastClose = document.getElementById("toastClose");

const runState = document.getElementById("runState");
const pidValue = document.getElementById("pidValue");
const uptimeValue = document.getElementById("uptimeValue");
const modelValue = document.getElementById("modelValue");
const configValue = document.getElementById("configValue");

const currentModelDisplay = document.getElementById("currentModelDisplay");
const currentConfigDisplay = document.getElementById("currentConfigDisplay");

const toggleInferenceBtn = document.getElementById("toggleInference");

const memValue = document.getElementById("memValue");
const cpuValue = document.getElementById("cpuValue");
const tempValue = document.getElementById("tempValue");

const refreshRateInput = document.getElementById("refreshRate");
const applyRefreshBtn = document.getElementById("applyRefresh");

const modelFileInput = document.getElementById("modelFile");
const modelNameInput = document.getElementById("modelName");
const uploadModelBtn = document.getElementById("uploadModel");

const configFileInput = document.getElementById("configFile");
const configNameInput = document.getElementById("configName");
const uploadConfigBtn = document.getElementById("uploadConfig");

const autoNameToggle = document.getElementById("autoName");

const downloadModelPathInput = document.getElementById("downloadModelPath");
const downloadConfigPathInput = document.getElementById("downloadConfigPath");
const downloadModelBtn = document.getElementById("downloadModel");
const downloadConfigBtn = document.getElementById("downloadConfig");

const listModelsBtn = document.getElementById("listModels");
const listConfigsBtn = document.getElementById("listConfigs");
const useModelBtn = document.getElementById("useModel");
const useConfigBtn = document.getElementById("useConfig");
const modelList = document.getElementById("modelList");
const configList = document.getElementById("configList");
const clearModelBtn = document.getElementById("clearModel");
const clearConfigBtn = document.getElementById("clearConfig");

const tailLinesInput = document.getElementById("tailLines");
const loadLogsBtn = document.getElementById("loadLogs");
const logOutput = document.getElementById("logOutput");

const historyLimitInput = document.getElementById("historyLimit");
const loadHistoryBtn = document.getElementById("loadHistory");
const historyTable = document.getElementById("historyTable");

const configEditor = document.getElementById("configEditor");
const loadConfigBtn = document.getElementById("loadConfig");
const saveConfigBtn = document.getElementById("saveConfig");
const deleteConfigBtn = document.getElementById("deleteConfig");

const netronFrame = document.getElementById("netronFrame");
const openNetronBtn = document.getElementById("openNetron");
const deleteModelBtn = document.getElementById("deleteModel");

const tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));
const tabsContainer = document.querySelector(".tabs-container");
const tabsDropdown = document.querySelector(".tabs-dropdown");
const tabsToggle = document.getElementById("tabsToggle");
const tabsMenu = document.getElementById("tabsMenu");

let autoRefreshTimer = null;
let telemetryChart = null;
let telemetryPoints = [];
let selectedModelPath = "";
let selectedConfigPath = "";
let inferenceRunning = false;
let configDirty = false;
let loadedConfigPath = "";
let loadedConfigContent = "";

// Current selections from API
let currentModel = "";
let currentConfig = "";

const defaultApiBase = "/api";
const savedApiBase = localStorage.getItem("piInferApiBase");

const defaultRefreshRate = 5;
const savedRefreshRate = localStorage.getItem("piInferRefreshRate");

const savedSelectedModelPath = localStorage.getItem("piInferSelectedModelPath");
const savedSelectedConfigPath = localStorage.getItem("piInferSelectedConfigPath");

const getInputValue = (element) => {
  if (!element) {
    return "";
  }
  if (typeof element.value === "string") {
    return element.value;
  }
  const attribute = element.getAttribute("value");
  return attribute || "";
};

const setInputValue = (element, value) => {
  if (!element) {
    return;
  }
  if (typeof element.value === "string") {
    element.value = value;
  } else {
    element.setAttribute("value", value);
  }
};

const buildTimestampedName = (filename, baseOverride = "") => {
  const safeName = baseOverride || filename || "file";
  const parts = safeName.split(".");
  const ext = parts.length > 1 ? `.${parts.pop()}` : "";
  const base = parts.join(".");
  const now = new Date();
  const stamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(
    now.getDate()
  ).padStart(2, "0")}_${String(now.getHours()).padStart(2, "0")}${String(
    now.getMinutes()
  ).padStart(2, "0")}${String(now.getSeconds()).padStart(2, "0")}`;
  return `${base}_${stamp}${ext}`;
};

// Check URL parameters for API base
const urlParams = new URLSearchParams(window.location.search);
const urlApiBase = urlParams.get("api");

apiBaseInput.value = urlApiBase || savedApiBase || getInputValue(apiBaseInput) || defaultApiBase;

setInputValue(refreshRateInput, savedRefreshRate || getInputValue(refreshRateInput) || String(defaultRefreshRate));

// Restore selected paths from localStorage
selectedModelPath = savedSelectedModelPath || "";
selectedConfigPath = savedSelectedConfigPath || "";

const setActiveTab = (tabId) => {
  tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabId);
  });
  tabPanels.forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.tab === tabId);
  });

  // Load data for the newly active tab
  if (tabId === 'models') {
    listModels().catch(console.error);
  } else if (tabId === 'configs') {
    listConfigs().catch(console.error);
  }
};

const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) {
    return "-";
  }
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  return `${hrs}h ${mins}m ${secs}s`;
};

const apiFetch = async (path, options = {}) => {
  const base = (getInputValue(apiBaseInput).trim() || defaultApiBase).replace(/\/+$/, "");
  const response = await fetch(`${base}${path}`, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  return response;
};

const resolveApiBaseUrl = () => {
  const base = getInputValue(apiBaseInput).trim() || defaultApiBase;
  if (base.startsWith("http")) {
    return base.replace(/\/+$/, "");
  }
  return `${window.location.origin}${base.startsWith("/") ? "" : "/"}${base.replace(
    /\/+$/,
    ""
  )}`;
};

const setAction = (message, tone = "muted") => {
  // Show toast
  toastMessage.textContent = message;
  toast.className = `toast ${tone}`;
  toast.style.display = "block";

  // Auto hide after 5 seconds
  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease-in";
    setTimeout(() => {
      toast.style.display = "none";
      toast.style.animation = "";
    }, 300);
  }, 5000);
};

const updateToggleButton = (running) => {
  toggleInferenceBtn.textContent = running ? "Stop Inference" : "Start Inference";
  toggleInferenceBtn.style.background = running
    ? "rgba(255, 122, 122, 0.2)"
    : "rgba(88, 214, 255, 0.2)";
  toggleInferenceBtn.style.color = running ? "var(--danger)" : "var(--primary)";
};

const updateStatus = async () => {
  const response = await apiFetch("/inference/status");
  const data = await response.json();
  inferenceRunning = Boolean(data.running);
  runState.textContent = data.running ? "Running" : "Stopped";
  runState.style.color = data.running ? "var(--primary)" : "var(--danger)";
  pidValue.textContent = data.pid ?? "-";
  uptimeValue.textContent = formatDuration(data.uptime);
  modelValue.textContent = data.current_model || "-";
  configValue.textContent = data.current_config || "-";
  if (currentModelDisplay) currentModelDisplay.textContent = data.current_model || "-";
  if (currentConfigDisplay) currentConfigDisplay.textContent = data.current_config || "-";
  updateToggleButton(inferenceRunning);
};

const updateTelemetry = async () => {
  const response = await apiFetch("/status/system");
  const data = await response.json();
  const memory = data.memory_usage || {};
  const cpu = data.cpu_load || {};
  const temp = data.temperature || {};
  memValue.textContent = `${memory.percent ?? 0}% (${Math.round(
    (memory.used || 0) / 1024 / 1024
  )} MB)`;
  cpuValue.textContent = `Load ${cpu.load1 ?? 0}, CPU ${cpu.cpu_percent ?? 0}%`;
  tempValue.textContent = `${temp.current ?? 0} C`;

  telemetryPoints.push({
    ts: new Date().toLocaleTimeString(),
    cpu: cpu.cpu_percent ?? 0,
    mem: memory.percent ?? 0,
    temp: temp.current ?? 0,
  });
  telemetryPoints = telemetryPoints.slice(-12);
  renderTelemetry();
};

const renderTelemetry = () => {
  const ctx = document.getElementById("telemetryChart");
  if (!telemetryChart) {
    telemetryChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: telemetryPoints.map((p) => p.ts),
        datasets: [
          {
            label: "CPU %",
            data: telemetryPoints.map((p) => p.cpu),
            borderColor: "#58d6ff",
            tension: 0.4,
          },
          {
            label: "Memory %",
            data: telemetryPoints.map((p) => p.mem),
            borderColor: "#f4bf6b",
            tension: 0.4,
          },
          {
            label: "Temp",
            data: telemetryPoints.map((p) => p.temp),
            borderColor: "#ff7a7a",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#c8d7e6" } },
        },
        scales: {
          x: { ticks: { color: "#9db2c4" } },
          y: { ticks: { color: "#9db2c4" } },
        },
      },
    });
  } else {
    telemetryChart.data.labels = telemetryPoints.map((p) => p.ts);
    telemetryChart.data.datasets[0].data = telemetryPoints.map((p) => p.cpu);
    telemetryChart.data.datasets[1].data = telemetryPoints.map((p) => p.mem);
    telemetryChart.data.datasets[2].data = telemetryPoints.map((p) => p.temp);
    telemetryChart.update();
  }
};

const refreshAll = async () => {
  try {
    await Promise.all([updateStatus(), updateTelemetry()]);
  } catch (error) {
    runState.textContent = "API Offline";
    runState.style.color = "var(--danger)";
    inferenceRunning = false;
    updateToggleButton(false);
  }
};

const startInference = async () => {
  const model = selectedModelPath;
  const config = selectedConfigPath;
  if (!model || !config) {
    setAction("Please select a model and config before starting inference.", "error");
    return;
  }
  const params = new URLSearchParams();
  if (model) params.set("model", model);
  if (config) params.set("config", config);
  const suffix = params.toString() ? `?${params}` : "";
  await apiFetch(`/inference/start${suffix}`, { method: "POST" });
  await refreshAll();
};

const stopInference = async () => {
  await apiFetch("/inference/stop", { method: "POST" });
  await refreshAll();
};

const listModels = async () => {
  const response = await apiFetch("/model/list");
  const data = await response.json();
  const filtered = (data.models || []).filter((pathValue) => !isHiddenPath(pathValue));
  renderModelList(filtered);
};

const listConfigs = async () => {
  const response = await apiFetch("/config/list");
  const data = await response.json();
  const filtered = (data.configs || []).filter((pathValue) => !isHiddenPath(pathValue));
  renderConfigList(filtered);
};

const loadLogs = async () => {
  const tail = getInputValue(tailLinesInput).trim();
  const params = new URLSearchParams();
  if (tail) params.set("tail", tail);
  const suffix = params.toString() ? `?${params}` : "";
  const response = await apiFetch(`/logs${suffix}`);
  const text = await response.text();
  logOutput.textContent = text || "No logs yet.";
  logOutput.scrollTop = logOutput.scrollHeight; // Auto-scroll logs
};

const uploadFile = async (endpoint, fileInput, nameInput, nameKey) => {
  if (!fileInput.files || !fileInput.files[0]) {
    throw new Error("Please select a file first.");
  }
  const params = new URLSearchParams();
  const name = getInputValue(nameInput).trim();
  const useTimestamp = autoNameToggle ? autoNameToggle.checked : true;
  const original = fileInput.files[0].name;
  const finalName = useTimestamp
    ? buildTimestampedName(original, name)
    : name || "";
  if (finalName) params.set(nameKey, finalName);
  const suffix = params.toString() ? `?${params}` : "";
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  const response = await apiFetch(`${endpoint}${suffix}`, {
    method: "POST",
    body: formData,
  });
  return response.json();
};

const uploadModelAndOpenNetron = async () => {
  const response = await uploadFile("/model/upload", modelFileInput, modelNameInput, "model");
  const modelPath = response.model;
  selectedModelPath = modelPath;
  const base = resolveApiBaseUrl();
  const modelUrl = `${base}/model/download?model=${encodeURIComponent(modelPath)}`;
  const netronUrl = `https://netron.app/?url=${encodeURIComponent(modelUrl)}`;
  window.open(netronUrl, "_blank", "noopener");
  setAction("Model uploaded and opened in Netron.", "ok");
  await listModels();
};

const isHiddenPath = (pathValue) => {
  const name = pathValue.split("/").pop() || "";
  return name.startsWith(".");
};

const selectModel = async (pathValue) => {
  const response = await apiFetch(`/model/select?model=${encodeURIComponent(pathValue)}`,
    { method: "POST" }
  );
  const data = await response.json();
  selectedModelPath = data.model;
  localStorage.setItem("piInferSelectedModelPath", selectedModelPath);
  // Update displays immediately
  modelValue.textContent = data.model || "-";
  if (currentModelDisplay) currentModelDisplay.textContent = data.model || "-";
  setAction("Current model updated.", "ok");
  await refreshAll();
};

const selectConfig = async (pathValue) => {
  const response = await apiFetch(`/config/select?config=${encodeURIComponent(pathValue)}`,
    { method: "POST" }
  );
  const data = await response.json();
  selectedConfigPath = data.config;
  localStorage.setItem("piInferSelectedConfigPath", selectedConfigPath);
  // Update displays immediately
  configValue.textContent = data.config || "-";
  if (currentConfigDisplay) currentConfigDisplay.textContent = data.config || "-";
  setAction("Current config updated.", "ok");
  await refreshAll();
};

const downloadFile = async (endpoint, paramName, pathValue) => {
  if (!pathValue) {
    throw new Error("Path is required.");
  }
  const params = new URLSearchParams();
  params.set(paramName, pathValue);
  const response = await apiFetch(`${endpoint}?${params.toString()}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = pathValue.split("/").pop() || "download";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

const renderModelList = (items) => {
  modelList.innerHTML = "";
  if (!items.length) {
    modelList.textContent = "No models found.";
    return;
  }
  const currentModelName = currentModel ? currentModel.split("/").pop() : null;
  items.forEach((pathValue) => {
    const row = document.createElement("div");
    row.className = "list-item";
    if (pathValue === currentModelName) {
      row.classList.add("current");
    }

    const label = document.createElement("span");
    label.className = "list-path";
    label.textContent = pathValue;
    label.addEventListener("click", () => {
      selectedModelPath = pathValue;
      setAction("Model selected.", "ok");
    });

    const actionWrap = document.createElement("div");
    const viewBtn = document.createElement("md-text-button");
    viewBtn.textContent = "View";
    viewBtn.addEventListener("click", () => {
      selectedModelPath = pathValue;
      const base = resolveApiBaseUrl();
      const modelUrl = `${base}/model/download?model=${encodeURIComponent(pathValue)}`;
      netronFrame.src = `https://netron.app/?url=${encodeURIComponent(modelUrl)}`;
      setAction("Netron viewer loaded.", "ok");
    });

    const dlBtn = document.createElement("md-text-button");
    dlBtn.textContent = "Download";
    dlBtn.addEventListener("click", () => {
      downloadFile("/model/download", "model", pathValue).catch((error) =>
        setAction(error.message, "error")
      );
    });

    const useBtn = document.createElement("md-text-button");
    useBtn.textContent = "Set Current";
    useBtn.addEventListener("click", () =>
      selectModel(pathValue).catch((error) => setAction(error.message, "error"))
    );

    const delBtn = document.createElement("md-text-button");
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", () => deleteModel(pathValue));

    actionWrap.appendChild(viewBtn);
    actionWrap.appendChild(dlBtn);
    actionWrap.appendChild(useBtn);
    actionWrap.appendChild(delBtn);
    row.appendChild(label);
    row.appendChild(actionWrap);
    modelList.appendChild(row);
  });
};

const renderConfigList = (items) => {
  configList.innerHTML = "";
  if (!items.length) {
    configList.textContent = "No configs found.";
    return;
  }
  const currentConfigName = currentConfig ? currentConfig.split("/").pop() : null;
  items.forEach((pathValue) => {
    const row = document.createElement("div");
    row.className = "list-item";
    if (pathValue === currentConfigName) {
      row.classList.add("current");
    }

    const label = document.createElement("span");
    label.className = "list-path";
    label.textContent = pathValue;
    label.addEventListener("click", () => {
      selectedConfigPath = pathValue;
      setAction("Config selected.", "ok");
    });

    const actionWrap = document.createElement("div");
    const editBtn = document.createElement("md-text-button");
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => loadConfigContent(pathValue));

    const dlBtn = document.createElement("md-text-button");
    dlBtn.textContent = "Download";
    dlBtn.addEventListener("click", () => {
      downloadFile("/config/download", "config", pathValue).catch((error) =>
        setAction(error.message, "error")
      );
    });

    const useBtn = document.createElement("md-text-button");
    useBtn.textContent = "Set Current";
    useBtn.addEventListener("click", () =>
      selectConfig(pathValue).catch((error) => setAction(error.message, "error"))
    );

    const delBtn = document.createElement("md-text-button");
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", () => deleteConfig(pathValue));

    actionWrap.appendChild(editBtn);
    actionWrap.appendChild(dlBtn);
    actionWrap.appendChild(useBtn);
    actionWrap.appendChild(delBtn);
    row.appendChild(label);
    row.appendChild(actionWrap);
    configList.appendChild(row);
  });
};

const loadConfigContent = async (pathValue) => {
  if (configDirty && loadedConfigPath) {
    const proceed = window.confirm(
      "You have unsaved changes. Discard and reload?"
    );
    if (!proceed) {
      return;
    }
  }
  selectedConfigPath = pathValue;
  const response = await apiFetch(
    `/config/download?config=${encodeURIComponent(pathValue)}&ts=${Date.now()}`,
    { cache: "no-store" }
  );
  const text = await response.text();
  configEditor.value = text;
  loadedConfigPath = pathValue;
  loadedConfigContent = text;
  configDirty = false;
  setAction("Config loaded into editor.", "ok");
};

const saveConfigContent = async () => {
  const target = selectedConfigPath;
  if (!target) {
    throw new Error("Select a config to save.");
  }
  const response = await apiFetch(`/config/update?config=${encodeURIComponent(target)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: configEditor.value || "" }),
  });
  const data = await response.json();
  loadedConfigPath = target;
  loadedConfigContent = configEditor.value || "";
  configDirty = false;
  setAction(`Saved ${data.config}`, "ok");
  await listConfigs();
};

const deleteModel = async (pathValue) => {
  await apiFetch(`/model/delete?model=${encodeURIComponent(pathValue)}`, { method: "POST" });
  if (selectedModelPath === pathValue) {
    selectedModelPath = "";
  }
  setAction("Model deleted.", "ok");
  await listModels();
};

const deleteConfig = async (pathValue) => {
  await apiFetch(`/config/delete?config=${encodeURIComponent(pathValue)}`, { method: "POST" });
  if (selectedConfigPath === pathValue) {
    selectedConfigPath = "";
    configEditor.value = "";
  }
  setAction("Config deleted.", "ok");
  await listConfigs();
};

const loadHistory = async () => {
  const limit = Number.parseInt(getInputValue(historyLimitInput), 10) || 10;
  const response = await apiFetch(`/history?limit=${limit}`);
  const data = await response.json();
  const items = data.history || [];
  historyTable.innerHTML = "";
  const header = document.createElement("div");
  header.className = "history-row header";
  ["Start", "End", "Status", "Model", "Config"].forEach((text) => {
    const cell = document.createElement("div");
    cell.className = "history-cell";
    cell.textContent = text;
    header.appendChild(cell);
  });
  historyTable.appendChild(header);
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "history-row";
    const cell = document.createElement("div");
    cell.className = "history-cell";
    cell.textContent = "No history yet.";
    cell.style.gridColumn = "1 / -1";
    empty.appendChild(cell);
    historyTable.appendChild(empty);
    return;
  }
  items.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "history-row";
    [
      entry.start_time || "-",
      entry.end_time || "-",
      entry.status || "-",
      entry.model || "-",
      entry.config || "-",
    ].forEach((value) => {
      const cell = document.createElement("div");
      cell.className = "history-cell";
      cell.textContent = value;
      row.appendChild(cell);
    });
    historyTable.appendChild(row);
  });
};

const applyRefresh = () => {
  const value = Number.parseInt(getInputValue(refreshRateInput), 10);
  const intervalMs = Number.isFinite(value) && value > 0 ? value * 1000 : 5000;
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(() => {
    refreshAll().catch(console.error);
    loadLogs().catch(console.error);
    loadHistory().catch(console.error);
    // Only refresh lists for active tabs
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab) {
      if (activeTab.dataset.tab === 'models') {
        listModels().catch(console.error);
      } else if (activeTab.dataset.tab === 'configs') {
        listConfigs().catch(console.error);
      }
    }
  }, intervalMs);
  refreshAll().catch(console.error);
  loadLogs().catch(console.error);
  loadHistory().catch(console.error);
  // Load lists for initially active tab
  const activeTab = document.querySelector('.tab-btn.active');
  if (activeTab && activeTab.dataset.tab === 'models') {
    listModels().catch(console.error);
  }
  localStorage.setItem("piInferRefreshRate", String(value));
  setAction(`Auto refresh: ${Math.round(intervalMs / 1000)}s`, "ok");
};

saveApiBaseBtn.addEventListener("click", () => {
  localStorage.setItem("piInferApiBase", getInputValue(apiBaseInput).trim());
  refreshAll();
});

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setActiveTab(button.dataset.tab);
  });
});

toggleInferenceBtn.addEventListener("click", () => {
  if (inferenceRunning) {
    stopInference().catch((error) => setAction(error.message, "error"));
  } else {
    startInference().catch((error) => setAction(error.message, "error"));
  }
});

useModelBtn.addEventListener("click", () => {
  const model = selectedModelPath;
  if (!model) {
    setAction("Select a model first.", "error");
    return;
  }
  selectModel(model).catch((error) => setAction(error.message, "error"));
});

useConfigBtn.addEventListener("click", () => {
  const config = selectedConfigPath;
  if (!config) {
    setAction("Select a config first.", "error");
    return;
  }
  selectConfig(config).catch((error) => setAction(error.message, "error"));
});

listModelsBtn.addEventListener("click", () => listModels().catch(console.error));
listConfigsBtn.addEventListener("click", () => listConfigs().catch(console.error));
loadLogsBtn.addEventListener("click", () => loadLogs().catch(console.error));
applyRefreshBtn.addEventListener("click", applyRefresh);
refreshRateInput.addEventListener("change", applyRefresh);
loadHistoryBtn.addEventListener("click", () => loadHistory().catch(console.error));
loadConfigBtn.addEventListener("click", () => {
  const target = selectedConfigPath || getInputValue(configPathInput).trim();
  if (!target) {
    setAction("Select a config first.", "error");
    return;
  }
  loadConfigContent(target).catch((error) => setAction(error.message, "error"));
});
saveConfigBtn.addEventListener("click", () =>
  saveConfigContent().catch((error) => setAction(error.message, "error"))
);
deleteConfigBtn.addEventListener("click", () => {
  const target = selectedConfigPath;
  if (!target) {
    setAction("Select a config first.", "error");
    return;
  }
  deleteConfig(target).catch((error) => setAction(error.message, "error"));
});
deleteModelBtn.addEventListener("click", () => {
  const target = selectedModelPath;
  if (!target) {
    setAction("Select a model first.", "error");
    return;
  }
  deleteModel(target).catch((error) => setAction(error.message, "error"));
});
openNetronBtn.addEventListener("click", () => {
  const target = selectedModelPath;
  if (target) {
    const base = resolveApiBaseUrl();
    const modelUrl = `${base}/model/download?model=${encodeURIComponent(target)}`;
    const netronUrl = `https://netron.app/?url=${encodeURIComponent(modelUrl)}`;
    window.open(netronUrl, "_blank", "noopener");
    setAction("Netron opened in a new tab.", "ok");
    return;
  }
  if (modelFileInput.files && modelFileInput.files[0]) {
    uploadModelAndOpenNetron().catch((error) => setAction(error.message, "error"));
    return;
  }
  setAction("Select or upload a model first.", "error");
});
clearModelBtn.addEventListener("click", () => {
  selectedModelPath = "";
  localStorage.removeItem("piInferSelectedModelPath");
  setAction("Model selection cleared.", "ok");
});
clearConfigBtn.addEventListener("click", () => {
  selectedConfigPath = "";
  localStorage.removeItem("piInferSelectedConfigPath");
  configEditor.value = "";
  setAction("Config selection cleared.", "ok");
});

uploadModelBtn.addEventListener("click", () => {
  uploadFile("/model/upload", modelFileInput, modelNameInput, "model")
    .then((data) => {
      setAction(`Model uploaded: ${data.model}`, "ok");
      return listModels();
    })
    .catch((error) => setAction(error.message, "error"));
});

uploadConfigBtn.addEventListener("click", () => {
  uploadFile("/config/upload", configFileInput, configNameInput, "config")
    .then((data) => {
      setAction(`Config uploaded: ${data.config}`, "ok");
      return listConfigs();
    })
    .catch((error) => setAction(error.message, "error"));
});

downloadModelBtn.addEventListener("click", () => {
  downloadFile("/model/download", "model", getInputValue(downloadModelPathInput).trim())
    .then(() => setAction("Model download started.", "ok"))
    .catch((error) => setAction(error.message, "error"));
});

downloadConfigBtn.addEventListener("click", () => {
  downloadFile("/config/download", "config", getInputValue(downloadConfigPathInput).trim())
    .then(() => setAction("Config download started.", "ok"))
    .catch((error) => setAction(error.message, "error"));
});

applyRefresh();
setActiveTab("overview");

toastClose.addEventListener("click", () => {
  toast.style.animation = "slideOut 0.3s ease-in";
  setTimeout(() => {
    toast.style.display = "none";
    toast.style.animation = "";
  }, 300);
});

modelFileInput.addEventListener("change", () => { // Update label for model file input
  const label = document.getElementById("modelFileName");
  if (label) {
    label.textContent = modelFileInput.files?.[0]?.name || "No file selected.";
  }
});

configFileInput.addEventListener("change", () => { // Update label for config file input
  const label = document.getElementById("configFileName");
  if (label) {
    label.textContent = configFileInput.files?.[0]?.name || "No file selected.";
  }
});

configEditor.addEventListener("input", () => {
  const current = configEditor.value || "";
  configDirty = loadedConfigPath !== "" && current !== loadedConfigContent;
});

// Add click handlers for current model/config display
modelValue.addEventListener("click", () => {
  setActiveTab("models");
  setAction("Switched to Models tab to change current model.", "ok");
});

configValue.addEventListener("click", () => {
  setActiveTab("models");
  setAction("Switched to Models tab to change current config.", "ok");
});

// Dynamic tabs management for responsive design
const updateTabsVisibility = () => {
  if (!tabsContainer || !tabsDropdown || !tabsMenu) return;

  const tabs = document.querySelector(".tabs");
  const tabButtons = Array.from(tabs.querySelectorAll(".tab-btn"));
  const containerWidth = tabsContainer.offsetWidth;
  const tabGap = 10; // gap between tabs
  const minVisibleTabs = 3; // Always show at least 3 tabs

  let totalWidth = 0;
  let visibleCount = 0;

  // Clear existing dropdown items
  tabsMenu.innerHTML = "";

  // First pass: calculate widths and determine visibility
  const tabWidths = tabButtons.map(tab => {
    // Force layout calculation
    tab.style.display = "flex";
    const width = tab.offsetWidth;
    return width;
  });

  // Second pass: decide which tabs to show/hide
  for (let i = 0; i < tabButtons.length; i++) {
    const tab = tabButtons[i];
    const tabWidth = tabWidths[i] + tabGap;

    // Always show first minVisibleTabs, or if there's enough space
    if (i < minVisibleTabs || totalWidth + tabWidth <= containerWidth - 80) { // 80px for toggle button
      tab.style.display = "flex";
      totalWidth += tabWidth;
      visibleCount++;
    } else {
      // Move to dropdown
      tab.style.display = "none";
      const dropdownItem = document.createElement("button");
      dropdownItem.className = "tab-btn dropdown-item";
      dropdownItem.setAttribute("data-tab", tab.getAttribute("data-tab"));
      dropdownItem.setAttribute("role", "tab");
      dropdownItem.textContent = tab.textContent;
      if (tab.classList.contains("active")) {
        dropdownItem.classList.add("active");
      }
      tabsMenu.appendChild(dropdownItem);
    }
  }

  // Show/hide dropdown based on whether there are hidden tabs
  const hasHiddenTabs = tabsMenu.children.length > 0;
  tabsDropdown.style.display = hasHiddenTabs ? "block" : "none";
};

// Initialize tabs visibility
const initTabsManagement = () => {
  updateTabsVisibility();

  // Update on window resize
  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(updateTabsVisibility, 100);
  });

  // Handle dropdown toggle
  if (tabsToggle) {
    tabsToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = tabsMenu.classList.contains("open");
      tabsMenu.classList.toggle("open");
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!tabsDropdown.contains(e.target)) {
      tabsMenu.classList.remove("open");
    }
  });

  // Handle dropdown item clicks
  tabsMenu.addEventListener("click", (e) => {
    if (e.target.classList.contains("tab-btn")) {
      const tabId = e.target.dataset.tab;
      setActiveTab(tabId);
      tabsMenu.classList.remove("open");
    }
  });
};

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initTabsManagement);
} else {
  initTabsManagement();
}

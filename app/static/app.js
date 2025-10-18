const serverUrl = document.body.dataset.serverUrl;
const serverUrlLabel = document.getElementById('server-url');
const refreshButton = document.getElementById('refresh-button');
const selectButton = document.getElementById('select-button');
const selectionStatus = document.getElementById('selection-status');
const modelListElement = document.getElementById('model-list');
const emptyStateElement = document.getElementById('empty-state');
const modelCountElement = document.getElementById('model-count');

let models = [];
let selectedModel = null;

function setLoading(isLoading) {
  refreshButton.disabled = isLoading;
  refreshButton.textContent = isLoading ? 'Chargement…' : 'Actualiser';
  if (isLoading) {
    selectionStatus.textContent = 'Chargement des modèles depuis LM Studio…';
  }
}

function renderModels() {
  modelListElement.innerHTML = '';
  modelCountElement.textContent = String(models.length);

  if (models.length === 0) {
    emptyStateElement.classList.remove('hidden');
    selectButton.disabled = true;
    selectedModel = null;
    return;
  }

  emptyStateElement.classList.add('hidden');

  models.forEach((model) => {
    const item = document.createElement('li');
    item.className = 'model-item';

    const label = document.createElement('label');
    label.className = 'model-label';

    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = 'model';
    radio.value = model.name;
    radio.addEventListener('change', () => {
      selectedModel = model.name;
      selectButton.disabled = false;
      selectionStatus.textContent = `Modèle sélectionné : ${model.name}`;
    });

    const title = document.createElement('span');
    title.className = 'model-name';
    title.textContent = model.name;

    label.appendChild(radio);
    label.appendChild(title);

    if (model.description) {
      const description = document.createElement('p');
      description.className = 'model-description';
      description.textContent = model.description;
      label.appendChild(description);
    }

    item.appendChild(label);
    modelListElement.appendChild(item);
  });
}

async function fetchModels() {
  setLoading(true);
  selectionStatus.textContent = 'Chargement des modèles depuis LM Studio…';
  try {
    const response = await fetch('/api/models');
    if (!response.ok) {
      throw new Error(`Erreur ${response.status}`);
    }
    const payload = await response.json();
    models = payload.models || [];
    renderModels();
    if (models.length === 0) {
      selectionStatus.textContent = "Aucun modèle disponible. Vérifiez votre serveur LM Studio.";
    } else {
      selectionStatus.textContent = 'Sélectionnez un modèle puis cliquez sur "Activer".';
    }
  } catch (error) {
    console.error('Impossible de récupérer les modèles', error);
    models = [];
    renderModels();
    selectionStatus.textContent =
      "Impossible de joindre LM Studio. Vérifiez que le serveur est démarré et accessible.";
  } finally {
    setLoading(false);
  }
}

async function submitSelection() {
  if (!selectedModel) {
    return;
  }

  selectButton.disabled = true;
  selectButton.textContent = 'Activation…';
  selectionStatus.textContent = `Activation du modèle ${selectedModel}…`;

  try {
    const response = await fetch('/api/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: selectedModel }),
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const message = payload.detail || `Erreur ${response.status}`;
      throw new Error(message);
    }

    const payload = await response.json();
    const message = payload.message || `Modèle ${selectedModel} activé.`;
    selectionStatus.textContent = message;
  } catch (error) {
    console.error("Impossible d'activer le modèle", error);
    selectionStatus.textContent =
      "L'activation du modèle a échoué. Vérifiez votre serveur LM Studio et réessayez.";
  } finally {
    selectButton.disabled = false;
    selectButton.textContent = 'Activer le modèle';
  }
}

function init() {
  serverUrlLabel.textContent = serverUrl;
  refreshButton.addEventListener('click', fetchModels);
  selectButton.addEventListener('click', submitSelection);
  fetchModels();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

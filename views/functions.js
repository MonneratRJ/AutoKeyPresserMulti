let api = null;
let translations = {};

function waitForApi() {
    return new Promise((resolve) => {
        const checkApi = () => {
            if (window.pywebview && window.pywebview.api) {
                api = window.pywebview.api;
                resolve();
            } else {
                setTimeout(checkApi, 100);
            }
        };
        checkApi();
    });
}

async function loadTranslations() {
    translations = await api.get_translations();
    updateUIText();
}

async function populateLanguageSelect() {
    const languages = await api.get_available_languages();
    const select = document.getElementById('languageSelect');
    select.innerHTML = languages.map(lang =>
        `<option value="${lang}">${lang.toUpperCase()}</option>`
    ).join('');
}

async function changeLanguage(langCode) {
    await api.set_language(langCode);
    await loadTranslations();
}

function updateUIText() {
    // Update all static text in the UI
    document.title = translations.app_title;
    document.getElementById('appTitle').textContent = translations.app_title;
    document.getElementById('languageLabel').textContent = translations.language;
    document.getElementById('labelKey').textContent = translations.key + ':';
    document.getElementById('labelInterval').textContent = translations.interval + ':';
    document.getElementById('addTimerBtn').textContent = translations.add;
    document.querySelector('button[onclick="startTimers()"]').textContent = translations.start;
    document.querySelector('button[onclick="stopTimers()"]').textContent = translations.stop;

    // Update table headers
    document.getElementById('thActive').textContent = translations.active;
    document.getElementById('thKey').textContent = translations.key;
    document.getElementById('thInterval').textContent = translations.interval;
    document.getElementById('thActions').textContent = translations.actions;

    // Update all remove buttons
    document.querySelectorAll('button.remove').forEach(btn => {
        btn.textContent = translations.remove;
    });
}

function disableUI() {
    // Disable inputs
    document.getElementById("keyInput").disabled = true;
    document.getElementById("intervalInput").disabled = true;

    // Disable add timer button
    const addButton = document.querySelector('button[onclick="addTimer()"]');
    if (addButton) addButton.disabled = true;

    // Disable all remove buttons and checkboxes
    document.querySelectorAll('table input[type="checkbox"], table button.remove').forEach(el => {
        el.disabled = true;
    });

    // Disable start button, enable stop button
    document.querySelector('button[onclick="startTimers()"]').disabled = true;
    document.querySelector('button[onclick="stopTimers()"]').disabled = false;
}

function enableUI() {
    // Enable inputs
    document.getElementById("keyInput").disabled = false;
    document.getElementById("intervalInput").disabled = false;

    // Enable add timer button
    const addButton = document.querySelector('button[onclick="addTimer()"]');
    if (addButton) addButton.disabled = false;

    // Enable all remove buttons and checkboxes
    document.querySelectorAll('table input[type="checkbox"], table button.remove').forEach(el => {
        el.disabled = false;
    });

    // Enable start button, disable stop button
    document.querySelector('button[onclick="startTimers()"]').disabled = false;
    document.querySelector('button[onclick="stopTimers()"]').disabled = true;
}

async function updateTimerList() {
    try {
        await waitForApi();
        const timerList = await api.get_timers();
        const container = document.getElementById("timerList");
        container.innerHTML = "";

        timerList.forEach((timer) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>
                    <input type="checkbox" 
                           ${timer.is_active ? "checked" : ""} 
                           onchange="toggleTimer('${timer.key}')">
                </td>
                <td>${timer.key}</td>
                <td>${timer.interval}</td>
                <td>
                    <button class="remove" onclick="removeTimer('${timer.key}')">${translations.remove}</button>
                </td>
            `;
            container.appendChild(row);
        });
    } catch (error) {
        console.error('Error updating timer list:', error);
    }
}

async function addTimer() {
    try {
        await waitForApi();
        const key = document.getElementById("keyInput").value;
        const interval = document.getElementById("intervalInput").value;

        if (!key || !interval) {
            alert("Please enter both key and interval");
            return;
        }

        await api.add_timer(key, interval);
        document.getElementById("keyInput").value = "";
        await updateTimerList();
    } catch (error) {
        console.error('Error adding timer:', error);
    }
}

async function removeTimer(key) {
    try {
        await waitForApi();
        await api.remove_timer(key);
        await updateTimerList();
    } catch (error) {
        console.error('Error removing timer:', error);
    }
}

async function toggleTimer(key) {
    try {
        await waitForApi();
        await api.toggle_timer(key);
        await updateTimerList();
    } catch (error) {
        console.error('Error toggling timer:', error);
    }
}

async function startTimers() {
    disableUI();
    try {
        await waitForApi();
        await api.start_timers();
        console.log('Timers started');
    } catch (error) {
        console.error('Error starting timers:', error);
        enableUI();
    }
}

async function stopTimers() {
    enableUI();
    try {
        await waitForApi();
        await api.stop_timers();
        console.log('Timers stopped');
    } catch (error) {
        console.error('Error stopping timers:', error);
        disableUI();
    }
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', async () => {
    await waitForApi();
    await populateLanguageSelect();
    await loadTranslations();
    await updateTimerList();
    enableUI();
});
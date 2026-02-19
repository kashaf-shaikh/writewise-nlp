/**
 * spell_popup.js
 *
 * Responsibilities:
 * - Render contextual popup for spelling suggestions
 * - Handle suggestion click
 * - Handle ignore action
 * - Close popup safely
 *
 * NOTE:
 * - No backend calls here
 * - Uses spell issues already returned by /predict
 * - Works with contenteditable editor
 */

// Active popup reference (only one popup at a time)
window.activeSpellPopup = null;

/**
 * Shows spelling suggestion popup near the clicked word
 *
 * @param {Object} issue - spelling issue object from backend
 * @param {HTMLElement} target - clicked span element
 */
function showSpellPopup(issue, target) {

    // Close existing popup if any
    closeSpellPopup();

    // Create popup container
    const popup = document.createElement("div");
    popup.className = "spell-popup";

    // Add suggestions
    if (issue.suggestions && issue.suggestions.length > 0) {
        issue.suggestions.slice(0, 3).forEach(suggestion => {

            const item = document.createElement("div");
            item.className = "spell-popup-item";
            item.innerText = "✔ " + suggestion;

            item.addEventListener("click", function () {
                applySpellSuggestion(issue, suggestion);
            });

            popup.appendChild(item);
        });
    }

    // Divider
    const divider = document.createElement("div");
    divider.className = "spell-popup-divider";
    popup.appendChild(divider);

    // Ignore option
    const ignoreItem = document.createElement("div");
    ignoreItem.className = "spell-popup-item spell-popup-ignore";
    ignoreItem.innerText = "✖ Ignore";

    ignoreItem.addEventListener("click", function () {
        ignoreSpellIssue(issue);
    });

    popup.appendChild(ignoreItem);

    // Add popup to body
    document.body.appendChild(popup);

    // Position popup near the clicked word
    const rect = target.getBoundingClientRect();
    popup.style.top = rect.bottom + window.scrollY + 5 + "px";
    popup.style.left = rect.left + window.scrollX + "px";

    // Save global reference
    window.activeSpellPopup = popup;
} // ✅ THIS CLOSING BRACE WAS MISSING


/**
 * Applies selected spelling suggestion
 */
function applySpellSuggestion(issue, suggestion) {

    const editor = document.getElementById("textInput");
    const text = editor.innerText;

    const start = issue.start_index;
    const end = start + issue.length;

    const newText =
        text.substring(0, start) +
        suggestion +
        text.substring(end);

    editor.innerText = newText;

    window.spellIssues = window.spellIssues.filter(
        i => i.issue_id !== issue.issue_id
    );

    window.spellIssues.forEach(i => {
        if (i.start_index > start) {
            i.start_index += suggestion.length - issue.length;
        }
    });

    highlightSpellingErrors(newText, window.spellIssues);

    closeSpellPopup();
}


/**
 * Igores spelling issue
 */
function ignoreSpellIssue(issue) {
    const editor = document.getElementById("textInput");
    editor.innerText = editor.innerText;
    closeSpellPopup();
}


/**
 * Removes popup safely
 */
function closeSpellPopup() {
    if (!window.activeSpellPopup) return;

    window.activeSpellPopup.remove();
    window.activeSpellPopup = null;
}


/* ============================
   STEP 1.1 — CLICK OUTSIDE CLOSE
   ============================ */
document.addEventListener("click", function (event) {
    if (!window.activeSpellPopup) return;

    const popup = window.activeSpellPopup;
    const clickedInsidePopup = popup.contains(event.target);
    const clickedSpellWord = event.target.classList.contains("spell-error");

    if (!clickedInsidePopup && !clickedSpellWord) {
        closeSpellPopup();
    }
});


/* ============================
   STEP 1.2 — ESC KEY CLOSE
   ============================ */
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && window.activeSpellPopup) {
        closeSpellPopup();
    }
});

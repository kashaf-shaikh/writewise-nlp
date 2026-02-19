/**
 * script.js
 *
 * Frontend logic for Intelligent Text Quality Analyzer.
 *
 * Responsibilities:
 * - Read user input from textarea
 * - Send text to Flask backend (/predict)
 * - Display prediction results
 * - Handle validation errors and warnings
 *
 * IMPORTANT:
 * - This file contains NO ML logic
 * - It only communicates with Flask API
 */

function analyzeText() {
    const textInput = document.getElementById("textInput");
    const resultDiv = document.getElementById("result");

    const text = textInput.innerText;

    resultDiv.innerHTML = "";

    if (text.length === 0) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger mt-3">
                ❌ Please enter some text before analyzing.
            </div>
        `;
        return;
    }

    resultDiv.innerHTML = `
        <div class="alert alert-info mt-3">
            ⏳ Analyzing text, please wait...
        </div>
    `;

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            resultDiv.innerHTML = `
                <div class="alert alert-danger mt-3">
                    ❌ ${data.message}
                </div>
            `;
            return;
        }

        // -----------------------------
        // Main Result Card
        // -----------------------------
        let warningHTML = "";
        if (!data.is_confident) {
            warningHTML = `
                <div class="alert alert-warning mt-2">
                    ⚠️ Low confidence prediction.
                </div>
            `;
        }

        resultDiv.innerHTML = `
            <div class="result-card p-3 mt-3">
                <h5 class="mb-2">📊 Text Quality Result</h5>
                <p class="mb-1">
                    <strong>Predicted Grade:</strong>
                    <span class="badge bg-success fs-6">
                        ${data.predicted_grade}
                    </span>
                </p>
                <p class="mb-1">
                    <strong>Confidence:</strong>
                    ${data.confidence}%
                </p>
                ${warningHTML}
            </div>
        `;

        // -----------------------------
        // Phase 2: Writing Style
        // -----------------------------
        resultDiv.innerHTML += `
            <div class="alert alert-info mt-3">
                ✍️ <strong>Writing Style:</strong>
                ${data.writing_style || "unknown"}
            </div>
        `;

        // -----------------------------
        // Phase 2: Language Issues (RIGHT PANEL)
        // -----------------------------
        const issuesList = document.getElementById("issuesList");

        // Clear previous issues
        issuesList.innerHTML = "";

        if (data.language_issues && data.language_issues.length > 0) {

            data.language_issues.forEach((issue, index) => {

                const issueHTML = `
                    <div class="issue-item">
                        <div class="issue-title">
                            Issue ${index + 1}: ${issue.type || "Language"}
                        </div>
                        <div class="issue-context">
                            ${issue.message || "Language issue detected."}
                        </div>
                        ${issue.word ? `<div><strong>Word:</strong> ${issue.word}</div>` : ""}
                        <div><strong>Severity:</strong> ${issue.severity || "medium"}</div>
                    </div>
                `;

                issuesList.innerHTML += issueHTML;
            });

        } else {

            issuesList.innerHTML = `
                <p class="text-muted">
                    ✅ No significant language issues detected.
                </p>
            `;
        }

        // -----------------------------
        // Store ALL spelling-related issues for popup (issues with suggestions)
        window.spellIssues = data.language_issues
            ? data.language_issues.filter(
                issue => issue.suggestions && issue.suggestions.length > 0
              )
            : [];



        // -----------------------------
        // Part 2: Highlight spelling errors in editor
        // -----------------------------
        highlightSpellingErrors(text, data.language_issues);

        // -----------------------------
        // FEATURE 5: Update Writing Overview
        // -----------------------------
        updateWritingOverview(
            text,
            data.language_issues
        );


    })
    .catch(error => {
        resultDiv.innerHTML = `
            <div class="alert alert-danger mt-3">
                ❌ Unable to connect to the server.
            </div>
        `;
        console.error("API Error:", error);


    });
}



/**
 * Highlight spelling errors inside the editor using backend indices
 */
function highlightSpellingErrors(text, issues) {

    if (!issues || issues.length === 0) {
        return;
    }

    // Filter only spelling issues
    const spellingIssues = issues
        .filter(issue =>
            issue.issue_type === "spelling" ||
            issue.type === "spelling"
        )
        .sort((a, b) => a.start_index - b.start_index);

    if (spellingIssues.length === 0) {
        return;
    }

    let resultHTML = "";
    let lastIndex = 0;

    spellingIssues.forEach(issue => {
        const start = issue.start_index;
        const end = start + issue.length; // ✅ FIX 1

        // Normal text before error
        resultHTML += text.substring(lastIndex, start);

        // Misspelled word with REQUIRED attributes
        resultHTML += `
            <span class="spell-error"
                  data-issue-id="${issue.issue_id}">
                ${text.substring(start, end)}
            </span>
        `;

        lastIndex = end;
    });

    // Remaining text
    resultHTML += text.substring(lastIndex);

    document.getElementById("textInput").innerHTML = resultHTML;
}




/* =========================================================
   APPLY SUGGESTION (ON BUTTON CLICK)
   ---------------------------------------------------------
   issueId    : ID of the spelling issue
   suggestion : selected correction word
   ========================================================= */
//function applySuggestion(issueId, suggestion) {
//
//    const editor = document.getElementById("textInput");
//
//    // 1️⃣ Find issue index
//    const issueIndex = window.spellIssues.findIndex(
//        i => i.issue_id === issueId
//    );
//
//    if (issueIndex === -1) return;
//
//    const issue = window.spellIssues[issueIndex];
//
//    // 2️⃣ Get current plain text
//    const text = editor.innerText;
//
//    const start = issue.start_index;
//    const end = start + issue.length;
//
//    // 3️⃣ Replace only selected word
//    const newText =
//        text.substring(0, start) +
//        suggestion +
//        text.substring(end);
//
//    // 4️⃣ Update editor text
//    editor.innerText = newText;
//
//    // 5️⃣ Remove the fixed issue
//    window.spellIssues.splice(issueIndex, 1);
//
//    // 6️⃣ Adjust remaining issue indexes
//    window.spellIssues.forEach(i => {
//        if (i.start_index > start) {
//            i.start_index += suggestion.length - issue.length;
//        }
//    });
//
//    // 7️⃣ Re-highlight remaining spelling errors
//    highlightSpellingErrors(newText, window.spellIssues);
//
//    if (typeof closeSpellPopup === "function") {
//        closeSpellPopup();
//    }
//
//
//}

/**
 * Global click handler for spelling error words
 *
 * Detects clicks on underlined spelling errors
 * and triggers contextual suggestion popup
 */
document.addEventListener("click", function (event) {

    // Only react to spelling error clicks
    if (!event.target.classList.contains("spell-error")) {
        return;
    }

    const issueId = event.target.getAttribute("data-issue-id");

    if (!issueId || !window.spellIssues) {
        return;
    }

    const issue = window.spellIssues.find(
        i => String(i.issue_id) === String(issueId)
    );

    if (!issue) {
        return;
    }

    // IMPORTANT: this function exists in spell_popup.js
    showSpellPopup(issue, event.target);
});


// STEP 5.2 — Update Writing Overview counts
function updateWritingOverview(text, languageIssues) {

    // --- Word Count ---
    const words = text.trim().length === 0
        ? []
        : text.trim().split(/\s+/);

    document.getElementById("wordCount").innerText = words.length;

    // --- Spelling Count ---
    const spellingCount = languageIssues
        ? languageIssues.filter(
            issue => issue.suggestions && issue.suggestions.length > 0
          ).length
        : 0;

    document.getElementById("spellingCount").innerText = spellingCount;

    // --- Grammar Count ---
    const grammarCount = languageIssues
        ? languageIssues.filter(
            issue => !issue.suggestions || issue.suggestions.length === 0
          ).length
        : 0;

    document.getElementById("grammarCount").innerText = grammarCount;

    // Show overview panel
    document.getElementById("writingOverview").style.display = "block";
}


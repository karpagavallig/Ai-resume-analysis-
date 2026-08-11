// ========================================
// AI RESUME ANALYZER - JAVASCRIPT
// ========================================


// Get the file input
const fileInput = document.getElementById("resumeFile");

// Get the area where the file name will appear
const fileName = document.getElementById("fileName");


// ========================================
// SHOW SELECTED FILE
// ========================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            const file = this.files[0];

            fileName.textContent = "✓ Selected: " + file.name;

        } else {

            fileName.textContent = "";

        }

    });

}


// ========================================
// CHECK FILE TYPE
// ========================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length === 0) {
            return;
        }

        const file = this.files[0];

        const allowedTypes = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ];

        if (!allowedTypes.includes(file.type)) {

            alert("Please upload only PDF or DOCX files.");

            fileInput.value = "";

            fileName.textContent = "";
        }

    });

}
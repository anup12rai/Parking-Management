
/* =========================================
   PARKSMART - MAIN JAVASCRIPT
========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // -------------------------------------
    // 1. PASSWORD VISIBILITY
    // -------------------------------------

    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("togglePassword");

    if (passwordInput && togglePassword) {

        togglePassword.addEventListener("click", function () {

            const isPassword =
                passwordInput.type === "password";

            passwordInput.type = isPassword ? "text" : "password";

            const icon = togglePassword.querySelector("i");

            if (icon) {
                icon.classList.toggle("fa-eye", !isPassword);
                icon.classList.toggle("fa-eye-slash", isPassword);
            }

        });

    }


    // -------------------------------------
    // 2. AUTO DISMISS FLASH ALERTS
    // -------------------------------------

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            if (typeof bootstrap !== "undefined") {

                const alertInstance =
                    bootstrap.Alert.getOrCreateInstance(alert);

                alertInstance.close();

            }

        }, 5000);

    });


    // -------------------------------------
    // 3. CONFIRM ACTIONS
    // -------------------------------------

    const confirmElements =
        document.querySelectorAll("[data-confirm]");

    confirmElements.forEach(function (element) {

        element.addEventListener("click", function (event) {

            const message =
                element.getAttribute("data-confirm") ||
                "Are you sure you want to continue?";

            if (!window.confirm(message)) {
                event.preventDefault();
            }

        });

    });


    // -------------------------------------
    // 4. TABLE SEARCH
    // -------------------------------------

    const searchInputs =
        document.querySelectorAll("[data-table-search]");

    searchInputs.forEach(function (input) {

        const tableSelector =
            input.getAttribute("data-table-search");

        const table = document.querySelector(tableSelector);

        if (!table) return;

        input.addEventListener("input", function () {

            const searchValue =
                input.value.toLowerCase().trim();

            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const rowText =
                    row.textContent.toLowerCase();

                row.style.display =
                    rowText.includes(searchValue) ? "" : "none";

            });

        });

    });


    // -------------------------------------
    // 5. CURRENT DATE AND TIME
    // -------------------------------------

    const dateElement =
        document.getElementById("currentDateTime");

    function updateDateTime() {

        if (!dateElement) return;

        const now = new Date();

        dateElement.textContent =
            now.toLocaleString();

    }

    if (dateElement) {

        updateDateTime();

        setInterval(updateDateTime, 1000);

    }


    // -------------------------------------
    // 6. UPPERCASE VEHICLE NUMBER
    // -------------------------------------

    const vehicleNumber =
        document.querySelector('input[name="vehicle_number"]');

    if (vehicleNumber) {

        vehicleNumber.addEventListener("input", function () {

            const start = this.selectionStart;
            const end = this.selectionEnd;

            this.value = this.value.toUpperCase();

            this.setSelectionRange(start, end);

        });

    }


    // -------------------------------------
    // 7. PREVENT DOUBLE FORM SUBMISSION
    // -------------------------------------

    const forms = document.querySelectorAll(
        "form[data-prevent-double-submit]"
    );

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector('button[type="submit"]');

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

            }

        });

    });


    console.log("ParkSmart JavaScript loaded successfully.");

});

// ==============================================
// Staff Dashboard
// ==============================================

const departmentSelector =
    document.getElementById(
        "departmentSelector"
    );


if (departmentSelector) {

    departmentSelector.addEventListener(
        "change",
        function () {

            const department =
                departmentSelector.value;

            console.log(
                "Selected department:",
                department
            );

            /*
             * BACKEND CONNECTION LATER
             *
             * Eventually this will request
             * department-specific data:
             *
             * GET /api/dashboard?department=HR
             *
             */

        }
    );

}

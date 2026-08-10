// ==============================================
// Ticket Management
// ==============================================

const searchInput =
    document.getElementById("ticketSearch");

const departmentFilter =
    document.getElementById("departmentFilter");

const statusFilter =
    document.getElementById("statusFilter");

const priorityFilter =
    document.getElementById("priorityFilter");

const ticketRows =
    document.querySelectorAll(".ticket-row");

const noTickets =
    document.getElementById("noTickets");


// ==============================================
// FILTER TICKETS
// ==============================================

function filterTickets() {

    const search =
        searchInput.value.toLowerCase();

    const department =
        departmentFilter.value;

    const status =
        statusFilter.value;

    const priority =
        priorityFilter.value;

    let visibleTickets = 0;


    ticketRows.forEach(function(ticket) {

        const text =
            ticket.textContent.toLowerCase();

        const ticketDepartment =
            ticket.dataset.department;

        const ticketStatus =
            ticket.dataset.status;

        const ticketPriority =
            ticket.dataset.priority;


        const matchesSearch =
            text.includes(search);


        const matchesDepartment =
            department === "all" ||
            ticketDepartment === department;


        const matchesStatus =
            status === "all" ||
            ticketStatus === status;


        const matchesPriority =
            priority === "all" ||
            ticketPriority === priority;


        const shouldShow =
            matchesSearch &&
            matchesDepartment &&
            matchesStatus &&
            matchesPriority;


        if (shouldShow) {

            ticket.style.display = "grid";

            visibleTickets++;

        } else {

            ticket.style.display = "none";

        }

    });


    if (visibleTickets === 0) {

        noTickets.style.display = "block";

    } else {

        noTickets.style.display = "none";

    }

}


// ==============================================
// EVENT LISTENERS
// ==============================================

searchInput.addEventListener(
    "input",
    filterTickets
);


departmentFilter.addEventListener(
    "change",
    filterTickets
);


statusFilter.addEventListener(
    "change",
    filterTickets
);


priorityFilter.addEventListener(
    "change",
    filterTickets
);


// ==============================================
// OPEN TICKET
// ==============================================

const viewButtons =
    document.querySelectorAll(
        ".view-ticket-button"
    );


viewButtons.forEach(function(button) {

    button.addEventListener(
        "click",
        function() {

            const ticketId =
                button.dataset.ticket;

            /*
             * BACKEND CONNECTION LATER
             *
             * Eventually:
             *
             * window.location.href =
             * `ticket-details.html?id=${ticketId}`;
             *
             */

            window.location.href =
                `ticket-details.html?id=${ticketId}`;

        }
    );

});


// ==============================================
// REFRESH
// ==============================================

const refreshButton =
    document.getElementById(
        "refreshTickets"
    );


refreshButton.addEventListener(
    "click",
    function() {

        location.reload();

    }
);

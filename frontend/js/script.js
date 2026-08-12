/* =========================================================
   TICKETGENIE - MAIN JAVASCRIPT
========================================================= */


/* =========================================================
   TICKET STORAGE
========================================================= */

const STORAGE_KEY = "ticketGenieTickets";


/* Get tickets from browser storage */

function getTickets() {

    const tickets = localStorage.getItem(STORAGE_KEY);

    if (!tickets) {

        const defaultTickets = [

            {
                id: "HD-1024",
                title: "Payroll Issue",
                category: "Payroll",
                priority: "High",
                status: "In Progress",
                description: "Having an issue with my latest paycheck.",
                date: "2026-08-08",
                createdAt: "2026-08-08T10:00:00"
            },

            {
                id: "HD-1025",
                title: "Benefits Question",
                category: "Benefits",
                priority: "Medium",
                status: "Open",
                description: "I have a question about my benefits.",
                date: "2026-08-07",
                createdAt: "2026-08-07T10:00:00"
            },

            {
                id: "HD-1026",
                title: "Laptop Request",
                category: "IT Support",
                priority: "Low",
                status: "Resolved",
                description: "Requesting a replacement laptop.",
                date: "2026-08-05",
                createdAt: "2026-08-05T10:00:00"
            },

            {
                id: "HD-1027",
                title: "PTO Request",
                category: "Time Off",
                priority: "Medium",
                status: "Pending",
                description: "Requesting PTO.",
                date: "2026-08-04",
                createdAt: "2026-08-04T10:00:00"
            },

            {
                id: "HD-1028",
                title: "Expense Reimbursement",
                category: "Payroll",
                priority: "Low",
                status: "Resolved",
                description: "Submitting an expense reimbursement.",
                date: "2026-08-02",
                createdAt: "2026-08-02T10:00:00"
            }

        ];

        return defaultTickets;
    }

    return JSON.parse(tickets);
}


/* Save tickets */

function saveTickets(tickets) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(tickets)
    );

}


/* =========================================================
   GENERATE TICKET ID
========================================================= */

function generateTicketId() {

    const tickets = getTickets();

    let highestNumber = 1028;

    tickets.forEach(ticket => {

        const number = parseInt(
            ticket.id.replace("HD-", ""),
            10
        );

        if (!isNaN(number) && number > highestNumber) {

            highestNumber = number;

        }

    });

    return `HD-${highestNumber + 1}`;
}


/* =========================================================
   NEW REQUEST FORM
========================================================= */

function initializeNewRequestForm() {

    const form = document.querySelector(
        ".request-form-card form"
    );

    if (!form) return;


    form.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            /* =================================================
               GET FORM VALUES
            ================================================= */

            const titleElement =
                document.getElementById(
                    "ticketSubject"
                );

            const categoryElement =
                document.getElementById(
                    "ticketCategory"
                );

            const priorityElement =
                document.getElementById(
                    "ticketPriority"
                );

            const descriptionElement =
                document.getElementById(
                    "ticketDescription"
                );

            const preferredDateElement =
                document.getElementById(
                    "preferredDate"
                );


            const title =
                titleElement
                    ? titleElement.value.trim()
                    : "";


            const category =
                categoryElement
                    ? categoryElement.value
                    : "";


            const priority =
                priorityElement
                    ? priorityElement.value
                    : "";


            const description =
                descriptionElement
                    ? descriptionElement.value.trim()
                    : "";


            const preferredDate =
                preferredDateElement
                    ? preferredDateElement.value
                    : "";


            /* =================================================
               VALIDATION
            ================================================= */

            if (!title) {

                showFormError(
                    "Please enter a request title."
                );

                if (titleElement) {
                    titleElement.focus();
                }

                return;
            }


            if (!category) {

                showFormError(
                    "Please select a category."
                );

                if (categoryElement) {
                    categoryElement.focus();
                }

                return;
            }


            if (!priority) {

                showFormError(
                    "Please select a priority."
                );

                if (priorityElement) {
                    priorityElement.focus();
                }

                return;
            }


            if (!description) {

                showFormError(
                    "Please provide a description."
                );

                if (descriptionElement) {
                    descriptionElement.focus();
                }

                return;
            }


            /* =================================================
               REMOVE OLD ERROR
            ================================================= */

            const oldError =
                document.querySelector(
                    ".form-error-message"
                );

            if (oldError) {
                oldError.style.display = "none";
            }


            /* =================================================
               CREATE TICKET
            ================================================= */

            const newTicket = {

                id: generateTicketId(),

                title: title,

                category: category,

                priority: priority,

                status: "Open",

                description: description,

                date: preferredDate,

                createdAt:
                    new Date().toISOString()

            };


            /* =================================================
               SAVE TICKET
            ================================================= */

            const tickets = getTickets();

            tickets.unshift(newTicket);

            saveTickets(tickets);


            /* =================================================
               SHOW SUCCESS
            ================================================= */

            showSuccessMessage(
                newTicket
            );


            /* =================================================
               REDIRECT
            ================================================= */

            setTimeout(
                () => {

                    window.location.href =
                        "my-tickets.html";

                },
                3200
            );

        }
    );

}


/* =========================================================
   FORM ERROR
========================================================= */

function showFormError(message) {

    const error =
        document.getElementById(
            "formErrorMessage"
        );

    if (!error) return;

    error.textContent = message;

    error.style.display = "block";


    error.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


/* =========================================================
   SUCCESS MESSAGE
========================================================= */

function showSuccessMessage(ticket) {

    let success =
        document.getElementById(
            "ticketSuccessMessage"
        );


    if (!success) {

        success =
            document.createElement("div");

        success.id =
            "ticketSuccessMessage";

        success.className =
            "ticket-success-message";

        document.body.appendChild(
            success
        );

    }


    success.innerHTML = `

        <div class="success-icon">

            <i class="fa-solid fa-check"></i>

        </div>

        <div>

            <strong>
                Request submitted successfully
            </strong>

            <span>
                Ticket #${escapeHTML(ticket.id)}
                has been created.
            </span>

        </div>

    `;


    /* Force browser to render before animation */

    requestAnimationFrame(() => {

        success.classList.add(
            "show"
        );

    });


    /* Keep message visible */

    setTimeout(
        () => {

            success.classList.remove(
                "show"
            );

        },
        3000
    );

}


/* =========================================================
   MY TICKETS
========================================================= */

function initializeMyTickets() {

    const table =
        document.querySelector(
            ".tickets-table"
        );

    if (!table) return;


    renderTickets();


    /* =================================================
       SEARCH
    ================================================= */

    const searchInput =
        document.getElementById(
            "ticketSearch"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            renderTickets
        );

    }


    /* =================================================
       FILTERS
    ================================================= */

    const filters =
        document.querySelectorAll(
            ".ticket-filter"
        );


    filters.forEach(filter => {

        filter.addEventListener(
            "change",
            renderTickets
        );

    });

}


/* =========================================================
   RENDER TICKETS
========================================================= */

function renderTickets() {

    const table =
        document.querySelector(
            ".tickets-table"
        );

    if (!table) return;


    /* =================================================
       SEARCH
    ================================================= */

    const searchInput =
        document.getElementById(
            "ticketSearch"
        );


    const searchTerm =
        searchInput
            ? searchInput.value
                .toLowerCase()
                .trim()
            : "";


    /* =================================================
       FILTERS
    ================================================= */

    const statusFilter =
        document.getElementById(
            "ticketStatusFilter"
        );

    const priorityFilter =
        document.getElementById(
            "ticketPriorityFilter"
        );


    const statusValue =
        statusFilter
            ? statusFilter.value
            : "all";


    const priorityValue =
        priorityFilter
            ? priorityFilter.value
            : "all";


    let tickets =
        getTickets();


    /* =================================================
       SEARCH
    ================================================= */

    if (searchTerm) {

        tickets =
            tickets.filter(ticket => {

                return (

                    ticket.title
                        .toLowerCase()
                        .includes(searchTerm)

                    ||

                    ticket.id
                        .toLowerCase()
                        .includes(searchTerm)

                    ||

                    ticket.category
                        .toLowerCase()
                        .includes(searchTerm)

                );

            });

    }


    /* =================================================
       STATUS FILTER
    ================================================= */

    if (
        statusValue &&
        statusValue !== "all"
    ) {

        tickets =
            tickets.filter(
                ticket =>
                    ticket.status ===
                    statusValue
            );

    }


    /* =================================================
       PRIORITY FILTER
    ================================================= */

    if (
        priorityValue &&
        priorityValue !== "all"
    ) {

        tickets =
            tickets.filter(
                ticket =>
                    ticket.priority ===
                    priorityValue
            );

    }


    /* =================================================
       SORT (newest first)
    ================================================= */

    tickets.sort(
        (a, b) => {

            const dateA =
                new Date(
                    a.createdAt
                );

            const dateB =
                new Date(
                    b.createdAt
                );

            return dateB - dateA;

        }
    );


    /* =================================================
       KEEP TABLE HEADER
    ================================================= */

    const header =
        table.querySelector(
            ".table-header"
        );


    table.innerHTML = "";


    if (header) {

        table.appendChild(
            header
        );

    }


    /* =================================================
       DISPLAY TICKETS
    ================================================= */

    tickets.forEach(
        ticket => {

            const row =
                createTicketRow(
                    ticket
                );

            table.appendChild(
                row
            );

        }
    );


    /* =================================================
       EMPTY STATE
    ================================================= */

    if (tickets.length === 0) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "ticket-empty-state";


        empty.innerHTML = `

            <i class="fa-regular fa-folder-open"></i>

            <strong>
                No tickets found
            </strong>

            <span>
                Try changing your search
                or filters.
            </span>

        `;


        table.appendChild(
            empty
        );

    }


    updateTicketOverview();

}


/* =========================================================
   CREATE TICKET ROW
========================================================= */

function createTicketRow(ticket) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "table-row ticket-clickable";


    const icon =
        getTicketIcon(
            ticket.category
        );


    const updated =
        formatTicketDate(
            ticket.createdAt
        );


    row.innerHTML = `

        <div class="request-info">

            <div class="request-icon">

                <i class="${icon}"></i>

            </div>

            <div>

                <strong>
                    ${escapeHTML(
                        ticket.title
                    )}
                </strong>

                <span>
                    #${escapeHTML(
                        ticket.id
                    )}
                </span>

            </div>

        </div>


        <span>
            ${escapeHTML(
                ticket.category
            )}
        </span>


        <span class="status ${getStatusClass(
            ticket.status
        )}">

            ${escapeHTML(
                ticket.status
            )}

        </span>


        <span class="priority ${ticket.priority
            .toLowerCase()
            .replace(/\s+/g, "-")}">

            ${escapeHTML(
                ticket.priority
            )}

        </span>


        <span>
            ${updated}
        </span>

    `;


    row.addEventListener(
        "click",
        () => {

            showTicketDetails(
                ticket
            );

        }
    );


    return row;

}


/* =========================================================
   TICKET ICON
========================================================= */

function getTicketIcon(category) {

    const icons = {

        "IT Support":
            "fa-solid fa-display",

        "IT & Technology":
            "fa-solid fa-display",

        "Payroll":
            "fa-solid fa-receipt",

        "Payroll & Benefits":
            "fa-solid fa-receipt",

        "Benefits":
            "fa-solid fa-shield-heart",

        "Human Resources":
            "fa-solid fa-users",

        "Employee Services":
            "fa-solid fa-user",

        "Time Off":
            "fa-solid fa-calendar-check",

        "Access & Permissions":
            "fa-solid fa-lock",

        "Other":
            "fa-solid fa-file-lines"

    };


    return (
        icons[category]
        ||
        "fa-solid fa-file-lines"
    );

}


/* =========================================================
   STATUS CLASS
========================================================= */

function getStatusClass(status) {

    return String(status)
        .toLowerCase()
        .replace(/\s+/g, "-");

}


/* =========================================================
   DATE FORMAT
========================================================= */

function formatTicketDate(
    dateString
) {

    if (!dateString) {
        return "—";
    }


    const date =
        new Date(dateString);


    if (isNaN(date.getTime())) {
        return "—";
    }


    const now =
        new Date();


    const difference =
        now - date;


    const hours =
        difference / 3600000;


    if (hours >= 0 && hours < 24) {
        return "Today";
    }


    if (hours >= 24 && hours < 48) {
        return "Yesterday";
    }


    return date.toLocaleDateString(
        "en-US",
        {
            month: "short",
            day: "numeric"
        }
    );

}


/* =========================================================
   UPDATE TICKET COUNTS
========================================================= */

function updateTicketOverview() {

    const tickets =
        getTickets();


    const open =
        tickets.filter(
            ticket =>
                ticket.status ===
                "Open"
        ).length;


    const inProgress =
        tickets.filter(
            ticket =>

                ticket.status ===
                "In Progress"

                ||

                ticket.status ===
                "Pending"

        ).length;


    const resolved =
        tickets.filter(
            ticket =>
                ticket.status ===
                "Resolved"
        ).length;


    const openCount =
        document.getElementById(
            "openCount"
        );

    const inProgressCount =
        document.getElementById(
            "inProgressCount"
        );

    const resolvedCount =
        document.getElementById(
            "resolvedCount"
        );


    if (openCount) {
        openCount.textContent = open;
    }

    if (inProgressCount) {
        inProgressCount.textContent = inProgress;
    }

    if (resolvedCount) {
        resolvedCount.textContent = resolved;
    }


    /* =================================================
       RECENT TICKETS (index page)
    ================================================= */

    const recentTickets =
        document.getElementById(
            "recentTickets"
        );


    if (recentTickets) {

        recentTickets.innerHTML = "";


        tickets
            .slice(0, 5)
            .forEach(ticket => {

                const row =
                    createTicketRow(
                        ticket
                    );

                recentTickets.appendChild(
                    row
                );

            });

    }

}


/* =========================================================
   TICKET DETAILS MODAL
========================================================= */

function showTicketDetails(ticket) {

    const modal =
        document.createElement(
            "div"
        );


    modal.className =
        "ticket-modal";


    modal.innerHTML = `

        <div class="ticket-modal-content">

            <button
                class="ticket-modal-close"
                type="button"
                aria-label="Close ticket details"
            >

                <i class="fa-solid fa-xmark"></i>

            </button>


            <p class="eyebrow">
                TICKET #${escapeHTML(
                    ticket.id
                )}
            </p>


            <h2>
                ${escapeHTML(
                    ticket.title
                )}
            </h2>


            <div class="ticket-detail-grid">


                <div>

                    <span>
                        Category
                    </span>

                    <strong>
                        ${escapeHTML(
                            ticket.category
                        )}
                    </strong>

                </div>


                <div>

                    <span>
                        Priority
                    </span>

                    <strong class="priority ${ticket.priority
                        .toLowerCase()
                        .replace(/\s+/g, "-")}">

                        ${escapeHTML(
                            ticket.priority
                        )}

                    </strong>

                </div>


                <div>

                    <span>
                        Status
                    </span>

                    <strong class="status ${getStatusClass(
                        ticket.status
                    )}">

                        ${escapeHTML(
                            ticket.status
                        )}

                    </strong>

                </div>


                <div>

                    <span>
                        Preferred Date
                    </span>

                    <strong>
                        ${
                            ticket.date
                                ? formatPreferredDate(
                                    ticket.date
                                )
                                : "Not specified"
                        }
                    </strong>

                </div>


            </div>


            <div class="ticket-description">

                <span>
                    Description
                </span>

                <p>
                    ${escapeHTML(
                        ticket.description
                    )}
                </p>

            </div>


            <div class="ticket-modal-footer">

                <span>
                    Created
                    ${formatTicketDate(
                        ticket.createdAt
                    )}
                </span>


                <button
                    class="modal-close-button"
                    type="button"
                >
                    Close
                </button>

            </div>

        </div>

    `;


    document.body.appendChild(
        modal
    );


    requestAnimationFrame(
        () => {

            modal.classList.add(
                "show"
            );

        }
    );


    /* =================================================
       CLOSE MODAL
    ================================================= */

    const closeModal =
        () => {

            modal.classList.remove(
                "show"
            );


            setTimeout(
                () => {

                    modal.remove();

                },
                200
            );

        };


    const closeIcon =
        modal.querySelector(
            ".ticket-modal-close"
        );


    const closeButton =
        modal.querySelector(
            ".modal-close-button"
        );


    if (closeIcon) {

        closeIcon.addEventListener(
            "click",
            closeModal
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeModal
        );

    }


    modal.addEventListener(
        "click",
        event => {

            if (
                event.target === modal
            ) {

                closeModal();

            }

        }
    );


    document.addEventListener(
        "keydown",
        function escapeHandler(event) {

            if (
                event.key === "Escape"
            ) {

                closeModal();

                document.removeEventListener(
                    "keydown",
                    escapeHandler
                );

            }

        }
    );

}


/* =========================================================
   FORMAT PREFERRED DATE
========================================================= */

function formatPreferredDate(
    dateString
) {

    if (!dateString) {
        return "Not specified";
    }


    const date =
        new Date(
            dateString + "T00:00:00"
        );


    if (isNaN(date.getTime())) {
        return dateString;
    }


    return date.toLocaleDateString(
        "en-US",
        {
            weekday: "short",
            month: "short",
            day: "numeric",
            year: "numeric"
        }
    );

}


/* =========================================================
   GENIE AI AGENT
========================================================= */

function initializeGenie() {

    const genieChat =
        document.getElementById(
            "genieChat"
        );


    if (!genieChat) return;


    const genieInput =
        document.getElementById(
            "genieInput"
        );


    const genieSendButton =
        document.getElementById(
            "genieSendButton"
        );


    const closeButton =
        document.getElementById(
            "closeGenieButton"
        );


    const genieButton =
        document.getElementById(
            "genieButton"
        );


    /* =================================================
       OPEN GENIE
    ================================================= */

    function openGenie() {

        genieChat.classList.add(
            "open"
        );


        if (genieInput) {

            setTimeout(
                () => {

                    genieInput.focus();

                },
                100
            );

        }

    }


    /* =================================================
       CLOSE GENIE
    ================================================= */

    function closeGenie() {

        genieChat.classList.remove(
            "open"
        );

    }


    /* Floating Genie button */

    if (genieButton) {

        genieButton.addEventListener(
            "click",
            openGenie
        );

    }


    /* Close button */

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeGenie
        );

    }


    /* Sidebar / knowledge-base Genie link */

    const genieNav =
        document.querySelector(
            ".genie-nav-link"
        );


    if (genieNav) {

        genieNav.addEventListener(
            "click",
            event => {

                event.preventDefault();

                openGenie();

            }
        );

    }


    const knowledgeGenieButton =
        document.getElementById(
            "knowledgeGenieButton"
        );


    if (knowledgeGenieButton) {

        knowledgeGenieButton.addEventListener(
            "click",
            openGenie
        );

    }


    const openGenieFromRequest =
        document.getElementById(
            "openGenieFromRequest"
        );


    if (openGenieFromRequest) {

        openGenieFromRequest.addEventListener(
            "click",
            openGenie
        );

    }


    /* =================================================
       SEND GENIE MESSAGE
    ================================================= */

    function sendGenieMessage() {

        if (!genieInput) return;


        const message =
            genieInput.value.trim();


        if (!message) return;


        addGenieMessage(
            message,
            "user"
        );


        genieInput.value = "";


        /* Show thinking indicator */

        const thinking =
            addGenieThinking();


        setTimeout(
            () => {

                if (thinking) {
                    thinking.remove();
                }


                const response =
                    getGenieResponse(
                        message
                    );


                addGenieMessage(
                    response,
                    "agent"
                );

            },
            700
        );

    }


    if (genieSendButton) {

        genieSendButton.addEventListener(
            "click",
            sendGenieMessage
        );

    }


    if (genieInput) {

        genieInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key ===
                    "Enter"
                ) {

                    event.preventDefault();

                    sendGenieMessage();

                }

            }
        );

    }


    /* =================================================
       SUGGESTION BUTTONS
    ================================================= */

    const suggestions =
        document.querySelectorAll(
            ".genie-suggestion"
        );


    suggestions.forEach(
        suggestion => {

            suggestion.addEventListener(
                "click",
                () => {

                    const message =
                        suggestion.textContent.trim();


                    if (!message) return;


                    addGenieMessage(
                        message,
                        "user"
                    );


                    const thinking =
                        addGenieThinking();


                    setTimeout(
                        () => {

                            if (thinking) {
                                thinking.remove();
                            }


                            const response =
                                getGenieResponse(
                                    message
                                );


                            addGenieMessage(
                                response,
                                "agent"
                            );

                        },
                        700
                    );

                }
            );

        }
    );


    /* =================================================
       CLICK OUTSIDE GENIE
    ================================================= */

    document.addEventListener(
        "click",
        event => {

            if (
                !genieChat.classList.contains(
                    "open"
                )
            ) {
                return;
            }


            const clickedInside =
                genieChat.contains(
                    event.target
                );


            const clickedButton =
                genieButton &&
                genieButton.contains(
                    event.target
                );


            const clickedNav =
                genieNav &&
                genieNav.contains(
                    event.target
                );


            if (
                !clickedInside &&
                !clickedButton &&
                !clickedNav
            ) {

                closeGenie();

            }

        }
    );

}


/* =========================================================
   GENIE THINKING INDICATOR
========================================================= */

function addGenieThinking() {

    const messages =
        document.getElementById(
            "genieMessages"
        );


    if (!messages) return null;


    const thinking =
        document.createElement(
            "div"
        );


    thinking.className =
        "genie-message genie-thinking";


    thinking.innerHTML = `

        <div class="genie-message-avatar">

            <i class="fa-solid fa-wand-magic-sparkles"></i>

        </div>

        <div class="genie-bubble">

            <span>Genie is thinking...</span>

        </div>

    `;


    messages.appendChild(
        thinking
    );


    messages.scrollTop =
        messages.scrollHeight;


    return thinking;

}


/* =========================================================
   GENIE RESPONSES
========================================================= */

function getGenieResponse(message) {

    const text =
        message
            .toLowerCase()
            .trim();


    /* =================================================
       GREETING
    ================================================= */

    if (
        text.includes("hello")
        ||
        text.includes("hi")
        ||
        text.includes("hey")
        ||
        text === "genie"
    ) {

        return "Hi! I'm Genie, your AI support agent. I can help you find the right support category, answer common questions, or guide you through creating a request. What do you need help with?";

    }


    /* =================================================
       PAYROLL
    ================================================= */

    if (
        text.includes("payroll")
        ||
        text.includes("paycheck")
        ||
        text.includes("salary")
        ||
        text.includes("wages")
        ||
        text.includes("pay")
    ) {

        return "I can help with payroll questions. If you're experiencing an issue with your paycheck, select Payroll when creating a request and include the pay period and a description of the issue.";

    }


    /* =================================================
       IT SUPPORT
    ================================================= */

    if (
        text.includes("laptop")
        ||
        text.includes("computer")
        ||
        text.includes("wifi")
        ||
        text.includes("wi-fi")
        ||
        text.includes("internet")
        ||
        text.includes("password")
        ||
        text.includes("login")
        ||
        text.includes("log in")
        ||
        text.includes("software")
        ||
        text.includes("monitor")
        ||
        text.includes("keyboard")
        ||
        text.includes("mouse")
        ||
        text.includes("printer")
        ||
        text.includes("it help")
        ||
        text.includes("it issue")
    ) {

        return "This sounds like an IT Support request. If you've already tried basic troubleshooting and still need help, create a new request and select IT & Technology as the category. Be sure to include any error messages or screenshots.";

    }


    /* =================================================
       BENEFITS
    ================================================= */

    if (
        text.includes("benefit")
        ||
        text.includes("insurance")
        ||
        text.includes("health")
        ||
        text.includes("dental")
        ||
        text.includes("vision")
        ||
        text.includes("401k")
    ) {

        return "For benefits questions, the Payroll & Benefits category is usually the best choice. When submitting your request, include the specific benefit or plan you're asking about so the right team can assist you.";

    }


    /* =================================================
       TIME OFF
    ================================================= */

    if (
        text.includes("pto")
        ||
        text.includes("vacation")
        ||
        text.includes("leave")
        ||
        text.includes("time off")
        ||
        text.includes("day off")
    ) {

        return "For PTO or leave-related requests, select Time Off as your category when creating a new request. You can also include your preferred date in the request.";

    }


    /* =================================================
       ACCESS / PERMISSIONS
    ================================================= */

    if (
        text.includes("access")
        ||
        text.includes("permission")
        ||
        text.includes("permissions")
        ||
        text.includes("account")
    ) {

        return "For access or permission issues, select IT & Technology as your category. Include the system or application you need access to and explain what you're currently unable to access.";

    }


    /* =================================================
       CREATE TICKET
    ================================================= */

    if (
        text.includes("ticket")
        ||
        text.includes("request")
        ||
        text.includes("submit")
        ||
        text.includes("create")
    ) {

        return "I can help you create a support request. Select New Request from the sidebar, then provide a clear title, category, priority, description, and preferred date if needed. Once submitted, your request will appear under My Tickets.";

    }


    /* =================================================
       MY TICKETS
    ================================================= */

    if (
        text.includes("my ticket")
        ||
        text.includes("my tickets")
        ||
        text.includes("ticket status")
        ||
        text.includes("check my tickets")
        ||
        text.includes("status")
    ) {

        return "You can view your submitted requests by selecting My Tickets from the sidebar. There you can search, filter, and select a ticket to view its details.";

    }


    /* =================================================
       RESPONSE TIME
    ================================================= */

    if (
        text.includes("how long")
        ||
        text.includes("response")
        ||
        text.includes("when")
        ||
        text.includes("wait")
    ) {

        return "The typical response time for a support request is within 1-2 business days. You can check My Tickets to monitor the status of your request.";

    }


    /* =================================================
       FALLBACK
    ================================================= */

    return "I can help with IT & Technology, Payroll & Benefits, Time Off, Employee Services, or creating and tracking a support request. Tell me a little more about what you need help with.";

}


/* =========================================================
   ADD GENIE MESSAGE
========================================================= */

function addGenieMessage(
    message,
    sender
) {

    const messages =
        document.getElementById(
            "genieMessages"
        );


    if (!messages) return;


    const messageElement =
        document.createElement(
            "div"
        );


    if (
        sender === "user"
    ) {

        messageElement.className =
            "genie-message genie-message-user";


        messageElement.innerHTML = `

            <div class="genie-bubble">

                ${escapeHTML(
                    message
                )}

            </div>

        `;

    }

    else {

        messageElement.className =
            "genie-message";


        messageElement.innerHTML = `

            <div class="genie-message-avatar">

                <i class="fa-solid fa-wand-magic-sparkles"></i>

            </div>

            <div class="genie-bubble">

                ${escapeHTML(
                    message
                )}

            </div>

        `;

    }


    messages.appendChild(
        messageElement
    );


    messages.scrollTop =
        messages.scrollHeight;

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(value) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   KNOWLEDGE BASE
========================================================= */

function initializeKnowledgeBase() {

    const searchInput =
        document.getElementById("knowledgeSearch");

    const searchButton =
        document.getElementById("knowledgeSearchButton");

    const articles =
        document.querySelectorAll(".knowledge-article");

    const categories =
        document.querySelectorAll(".knowledge-category");


    if (!searchInput) return;


    function searchArticles() {

        const searchTerm =
            searchInput.value
                .toLowerCase()
                .trim();


        articles.forEach(article => {

            const articleText =
                article.textContent.toLowerCase();

            if (
                !searchTerm ||
                articleText.includes(searchTerm)
            ) {

                article.style.display = "flex";

            } else {

                article.style.display = "none";

            }

        });

    }


    if (searchButton) {

        searchButton.addEventListener(
            "click",
            searchArticles
        );

    }


    searchInput.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {

                event.preventDefault();

                searchArticles();

            }

        }
    );


    categories.forEach(category => {

        category.addEventListener(
            "click",
            () => {

                const selectedCategory =
                    category.dataset.category;


                articles.forEach(article => {

                    const articleCategory =
                        article.dataset.category;


                    if (
                        articleCategory ===
                        selectedCategory
                    ) {

                        article.style.display = "flex";

                    } else {

                        article.style.display = "none";

                    }

                });


                searchInput.value =
                    selectedCategory;

            }
        );

    });

}


/* =========================================================
   INITIALIZE EVERYTHING
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeNewRequestForm();

        initializeMyTickets();

        initializeGenie();

        initializeKnowledgeBase();

        updateTicketOverview();

    }

    

);

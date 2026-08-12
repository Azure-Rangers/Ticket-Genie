/* =========================================================
   TICKETGENIE - MAIN JAVASCRIPT & BACKEND API CLIENT
========================================================= */

const API_BASE_URL = "/api";

/* =========================================================
   BACKEND API CLIENT
========================================================= */

async function apiFetchTickets(params = {}) {
    try {
        const query = new URLSearchParams();
        if (params.search) query.append("search", params.search);
        if (params.status && params.status !== "all") query.append("status", params.status);
        if (params.priority && params.priority !== "all") query.append("priority", params.priority);

        const url = query.toString() ? `${API_BASE_URL}/tickets?${query.toString()}` : `${API_BASE_URL}/tickets`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        return Array.isArray(data) ? data : (data.tickets || []);
    } catch (err) {
        console.error("Failed to fetch tickets from backend API:", err);
        return [];
    }
}

async function apiCreateTicket(ticketPayload) {
    try {
        const res = await fetch(`${API_BASE_URL}/tickets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticketPayload)
        });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Failed to create ticket via backend API:", err);
        throw err;
    }
}

async function apiSendGenieChat(message) {
    try {
        const res = await fetch(`${API_BASE_URL}/genie/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Failed to send Genie chat message:", err);
        return { reply: "I'm having trouble connecting to the support service right now." };
    }
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

            /* =================================================
               CREATE & SAVE TICKET VIA BACKEND API
            ================================================= */

            const newTicketData = {
                title: title,
                category: category,
                priority: priority,
                department: category === "Payroll" || category === "Benefits" || category === "Time Off" ? "HR" : "IT",
                description: description,
                preferredDate: preferredDate
            };

            apiCreateTicket(newTicketData).then((savedTicket) => {
                showSuccessMessage(savedTicket);
                setTimeout(() => {
                    window.location.href = "my-tickets.html";
                }, 1200);
            });
            return;


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

async function renderTickets() {

    const table =
        document.querySelector(
            ".tickets-table"
        );

    if (!table) return;

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

    let tickets = await apiFetchTickets({
        search: searchTerm,
        status: statusValue,
        priority: priorityValue
    });


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

async function updateTicketOverview(providedTickets) {

    const tickets = providedTickets || await apiFetchTickets();


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

        apiSendGenieChat(message).then((response) => {
            if (thinking) {
                thinking.remove();
            }
            const replyText = response.reply || response;
            addGenieMessage(replyText, "agent");
        });

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

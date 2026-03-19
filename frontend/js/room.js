let currentRoomId = null;
let currentPrice = null;
let currentType = null;

function loadRooms() {
    fetch("http://127.0.0.1:5000/rooms")
        .then(res => res.json())
        .then(data => {
            let html = "";
            data.forEach(r => {
                let isAvailable = r.status === "AVAILABLE";
                let badgeClass = isAvailable ? "available" : "occupied";
                
                let buttonHtml = isAvailable 
                    ? `<button onclick="openModal(${r.id}, ${r.price}, '${r.type}')">Book</button>`
                    : `<button style="background: #e74c3c;" onclick="checkoutRoom(${r.id})">Checkout</button>`;

                html += `
                    <div class="card">
                        <span class="badge ${badgeClass}">${r.status}</span>
                        <img src="${r.image}" alt="${r.type} Room" style="width:100%; height:200px; object-fit:cover;">
                        <div class="card-content">
                            <h3>${r.type} Room</h3>
                            <p>₹${r.price} per night</p>
                            ${buttonHtml}
                        </div>
                    </div>
                `;
            });
            document.getElementById("rooms").innerHTML = html;
        })
        .catch(err => console.error("Error fetching rooms:", err));
}

window.openModal = function(id, price, type) {
    currentRoomId = id; currentPrice = price; currentType = type;
    document.getElementById("guestName").value = "";
    document.getElementById("guestPhone").value = "";
    document.getElementById("bookingModal").style.display = "block";
    document.getElementById("step1-form").style.display = "block";
    document.getElementById("step2-payment").style.display = "none";
    document.getElementById("step3-receipt").style.display = "none";
};

window.closeModal = function() {
    document.getElementById("bookingModal").style.display = "none";
};

window.goToPayment = function() {
    let name = document.getElementById("guestName").value;
    let phone = document.getElementById("guestPhone").value;
    if(!name || !phone) return alert("Please enter Name and Phone Number!"); 
    
    document.getElementById("step1-form").style.display = "none";
    document.getElementById("payAmount").innerText = currentPrice;
    document.getElementById("step2-payment").style.display = "block";
};

window.confirmBooking = function() {
    // 🚨 THIS IS OUR TEST POP-UP 🚨
    alert("The button works! Attempting to send data to Python...");

    let name = document.getElementById("guestName").value;
    let phone = document.getElementById("guestPhone").value;

    fetch("http://127.0.0.1:5000/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, phone: phone, room_id: currentRoomId })
    })
    .then(response => {
        if (!response.ok) {
            alert("Backend Error! Check your Python terminal for errors.");
            throw new Error("Server rejected the request.");
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("step2-payment").style.display = "none";
        document.getElementById("receiptData").innerHTML = `
            <p><strong>Name:</strong> ${name}</p>
            <p><strong>Phone:</strong> ${phone}</p>
            <hr style="border: 0.5px solid #ddd;">
            <p><strong>Room:</strong> ${currentType}</p>
            <p><strong>Paid:</strong> ₹${currentPrice}</p>
        `;
        document.getElementById("step3-receipt").style.display = "block";
    })
    .catch(err => {
        console.error("Fetch error:", err);
        alert("Failed to connect to the backend.");
    });
};

window.checkoutRoom = function(id) {
    if (confirm("Are you sure you want to checkout this room?")) {
        fetch("http://127.0.0.1:5000/checkout/" + id, { method: "POST" })
        .then(() => loadRooms())
        .catch(err => alert("Checkout Failed! Is the server running?"));
    }
};

window.closeAndReload = function() {
    closeModal();
    loadRooms(); 
};

// Initial load
loadRooms();
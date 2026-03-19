const form = document.getElementById("order-form");
const orderType = document.getElementById("order-type");
const priceField = document.getElementById("price-field");
const priceInput = document.getElementById("price");
const quantityInput = document.getElementById("quantity");
const symbolInput = document.getElementById("symbol");
const result = document.getElementById("result");
const spinner = document.getElementById("spinner");
const submitText = document.getElementById("submit-text");
const sideButtons = document.querySelectorAll(".side-btn");
const resultOrderId = document.getElementById("result-order-id");
const resultStatus = document.getElementById("result-status");
const resultQty = document.getElementById("result-qty");
const resultPrice = document.getElementById("result-price");
const resultMessage = document.getElementById("result-message");
const ordersBody = document.getElementById("orders-body");
const refreshOrdersBtn = document.getElementById("refresh-orders");

let selectedSide = "BUY";

function setSide(side) {
  selectedSide = side;
  sideButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.side === side);
  });
}

setSide("BUY");

orderType.addEventListener("change", () => {
  const isLimit = orderType.value === "LIMIT";
  priceField.classList.toggle("hidden", !isLimit);
  priceInput.disabled = !isLimit;
  if (!isLimit) {
    priceInput.value = "";
  }
});

sideButtons.forEach((button) => {
  button.addEventListener("click", () => setSide(button.dataset.side));
});

function setLoading(isLoading) {
  spinner.classList.toggle("hidden", !isLoading);
  submitText.textContent = isLoading ? "Placing..." : "Submit Order";
}

function setResultStatusClass(status, isError) {
  result.classList.remove("success", "error", "warn");
  if (isError) {
    result.classList.add("error");
    return;
  }
  if (status === "NEW") {
    result.classList.add("warn");
    return;
  }
  result.classList.add("success");
}

function renderResult(details, isError) {
  setResultStatusClass(details.status, isError);
  resultOrderId.textContent = details.orderId || "-";
  resultStatus.textContent = details.status || "-";
  resultQty.textContent = details.executedQty || "-";
  resultPrice.textContent = details.avgPrice || "-";
  resultMessage.textContent = details.message || "";
}

function renderError(message) {
  renderResult(
    {
      orderId: "-",
      status: "ERROR",
      executedQty: "-",
      avgPrice: "-",
      message,
    },
    true
  );
}

function isOpenOrder(status) {
  return status === "NEW" || status === "PARTIALLY_FILLED";
}

async function loadOrders() {
  try {
    const response = await fetch("/orders");
    const data = await response.json();
    if (!response.ok) {
      renderError(data.detail || "Failed to load orders.");
      return;
    }

    ordersBody.innerHTML = "";
    (data.orders || []).forEach((order) => {
      const row = document.createElement("tr");
      const price = order.price || order.avgPrice || "-";
      row.innerHTML = `
        <td>${order.symbol || "-"}</td>
        <td>${order.side || "-"}</td>
        <td>${order.type || "-"}</td>
        <td>${order.status || "-"}</td>
        <td>${order.origQty || order.executedQty || "-"}</td>
        <td>${price}</td>
        <td>
          ${isOpenOrder(order.status) ? `<button class="cancel-btn" data-symbol="${order.symbol}" data-id="${order.orderId}">Cancel</button>` : ""}
        </td>
      `;
      ordersBody.appendChild(row);
    });
  } catch (error) {
    renderError("Network error while loading orders.");
  }
}

ordersBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!target.classList.contains("cancel-btn")) {
    return;
  }

  const symbol = target.dataset.symbol;
  const orderId = Number(target.dataset.id);
  if (!symbol || !orderId) {
    renderError("Missing symbol or order ID for cancel.");
    return;
  }

  target.disabled = true;
  target.textContent = "Canceling...";

  try {
    const response = await fetch("/cancel-order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, orderId }),
    });
    const data = await response.json();
    if (!response.ok) {
      renderError(data.detail || "Cancel failed.");
    } else {
      renderResult(
        {
          orderId: data.orderId,
          status: data.status || "CANCELED",
          executedQty: data.executedQty || "-",
          avgPrice: data.avgPrice || "-",
          message: "Order canceled successfully.",
        },
        false
      );
      await loadOrders();
    }
  } catch (error) {
    renderError("Network error while canceling order.");
  } finally {
    target.disabled = false;
    target.textContent = "Cancel";
  }
});

refreshOrdersBtn.addEventListener("click", () => {
  loadOrders();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoading(true);

  const qtyValue = parseFloat(quantityInput.value);
  if (!qtyValue || qtyValue <= 0) {
    renderError("Quantity must be greater than 0.");
    setLoading(false);
    return;
  }

  if (orderType.value === "LIMIT" && !priceInput.value) {
    renderError("Price is required for LIMIT orders.");
    setLoading(false);
    return;
  }

  const payload = {
    symbol: symbolInput.value,
    side: selectedSide,
    type: orderType.value,
    quantity: qtyValue,
    price: priceInput.value ? parseFloat(priceInput.value) : null,
  };

  try {
    const response = await fetch("/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      renderError(data.detail || "Request failed");
      setLoading(false);
      return;
    }

    renderResult(data, false);
    await loadOrders();
  } catch (error) {
    renderError("Network error. Please try again.");
  } finally {
    setLoading(false);
  }
});

orderType.dispatchEvent(new Event("change"));
loadOrders();

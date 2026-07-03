function showToast(message) {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 2400);
}

function formatMoney(value) {
  return Number(value).toFixed(2);
}

function setFormMessage(el, message, type = "error") {
  if (!el) return;
  el.textContent = message;
  el.className = `form-msg ${type}`;
}

async function refreshCartCount() {
  const badge = document.querySelector("[data-cart-count]");
  if (!badge) return;
  if (!authToken()) {
    badge.textContent = "0";
    return;
  }
  try {
    const { items } = await api.getCart();
    const count = items.reduce((sum, i) => sum + i.quantity, 0);
    badge.textContent = String(count);
  } catch (_) {
    badge.textContent = "0";
  }
}

function renderAuthState() {
  const authSlot = document.querySelector("[data-auth-slot]");
  if (!authSlot) return;
  const user = currentUser();
  if (user) {
    authSlot.innerHTML = `
      <a href="orders.html" class="icon-link">${user.full_name.split(" ")[0]}</a>
      <button class="icon-link" style="background:none;border:none;cursor:pointer;font:inherit" data-logout>Log out</button>
    `;
    authSlot.querySelector("[data-logout]").addEventListener("click", logout);
  } else {
    authSlot.innerHTML = `<a href="login.html" class="icon-link">Log in</a>`;
  }
}

function productCardHTML(product) {
  return `
    <a class="product-card" href="product.html?id=${product.id}">
      <div class="product-thumb"><img src="${product.image_url}" alt="${product.name}" loading="lazy"></div>
      <div class="product-body">
        <span class="product-category">${product.category}</span>
        <span class="product-name">${product.name}</span>
        <div class="product-foot">
          <span class="spec-price">$${formatMoney(product.price)}</span>
          <span class="spec-tag">${product.spec_tag || ""}</span>
        </div>
      </div>
    </a>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  renderAuthState();
  refreshCartCount();

  const searchForm = document.querySelector("[data-search-form]");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const q = new FormData(searchForm).get("q");
      window.location.href = `products.html?q=${encodeURIComponent(q || "")}`;
    });
  }
});

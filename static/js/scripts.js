
        const menuBtn = document.getElementById("menuBtn");
        const mobileMenu = document.getElementById("mobileMenu");

        if (menuBtn && mobileMenu) {
            menuBtn.addEventListener("click", () => {
                mobileMenu.classList.toggle("hidden");
            });
        }

        // Mobile menu link click ke baad menu close
        document.querySelectorAll(".mobile-link").forEach(link => {
            link.addEventListener("click", () => {
                if (mobileMenu) mobileMenu.classList.add("hidden");
            });
        });




    // Product Data=========================


    const product = {
        name: "Premium Hair Growth Oil",
        price: 1499
    };


    // Elements
    const minusBtn = document.getElementById("minusBtn");
    const plusBtn = document.getElementById("plusBtn");
    const quantityElement = document.getElementById("quantity");
    const addToCartBtn = document.getElementById("addToCartBtn");
    const buyNowBtn = document.getElementById("buyNowBtn");

    const cartToast = document.getElementById("cartToast");
    const toastText = document.getElementById("toastText");
    const productPriceElement = document.getElementById("productPrice");
    const cartCountElement = document.getElementById("cartCount");

    // Modal Elements
    const cartBtn = document.getElementById("cartBtn");
    const cartModal = document.getElementById("cartModal");
    const cartBackdrop = document.getElementById("cartBackdrop");
    const closeCartBtn = document.getElementById("closeCartBtn");
    const cartItemsList = document.getElementById("cartItemsList");
    const cartSubtotal = document.getElementById("cartSubtotal");
    const cartCheckoutBtn = document.getElementById("cartCheckoutBtn");

    // Unit Price
    const unitPrice = productPriceElement 
        ? (parseFloat(productPriceElement.getAttribute("data-price")) || 1499)
        : 1499;

    // Quantity
    let quantity = 1;

    function updateDisplayPrice() {
        if (productPriceElement) {
            const totalPrice = Math.round(unitPrice * quantity);
            productPriceElement.textContent = `Rs. ${totalPrice}`;
        }
    }

    function getCart() {
        return JSON.parse(localStorage.getItem("hairGlowCart")) || [];
    }

    function saveCart(cart) {
        localStorage.setItem("hairGlowCart", JSON.stringify(cart));
        updateCartBadge();
        renderCartDrawer();
    }

    function updateCartBadge() {
        if (cartCountElement) {
            const cart = getCart();
            const totalItems = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
            cartCountElement.textContent = totalItems;
        }
    }

    function renderCartDrawer() {
        if (!cartItemsList || !cartSubtotal) return;
        const cart = getCart();

        if (cart.length === 0) {
            cartItemsList.innerHTML = `
                <div class="text-center py-12 text-gray-500">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto text-gray-300 mb-3">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835L5.91 7.5h12.18l1.272-3.665A1.125 1.125 0 0120.45 3h1.3M5.91 7.5l1.04 8.11a2.25 2.25 0 002.23 1.965h6.64a2.25 2.25 0 002.23-1.965l1.04-8.11M9 20.25h.008v.008H9v-.008zm6 0h.008v.008H15v-.008z" />
                    </svg>
                    <p class="font-medium text-base text-gray-700">Your cart is empty</p>
                    <p class="text-xs text-gray-400 mt-1">Add items to get started!</p>
                </div>
            `;
            cartSubtotal.textContent = "Rs. 0";
            return;
        }

        let total = 0;
        cartItemsList.innerHTML = cart.map((item, index) => {
            const itemTotal = (item.price || unitPrice) * (item.quantity || 1);
            total += itemTotal;
            return `
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl border border-gray-100">
                    <div>
                        <h4 class="font-semibold text-gray-900 text-sm">${item.name}</h4>
                        <p class="text-xs text-green-700 font-bold mt-1">Rs. ${itemTotal}</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="flex items-center border border-gray-200 bg-white rounded-full overflow-hidden">
                            <button onclick="changeCartQty(${index}, -1)" class="w-7 h-7 flex items-center justify-center text-sm hover:bg-gray-100 transition">-</button>
                            <span class="w-6 text-center text-xs font-bold">${item.quantity}</span>
                            <button onclick="changeCartQty(${index}, 1)" class="w-7 h-7 flex items-center justify-center text-sm hover:bg-gray-100 transition">+</button>
                        </div>
                        <button onclick="removeFromCart(${index})" class="text-red-500 hover:text-red-700 text-xs font-bold p-1">✕</button>
                    </div>
                </div>
            `;
        }).join('');

        cartSubtotal.textContent = `Rs. ${total}`;
    }

    window.changeCartQty = function(index, delta) {
        let cart = getCart();
        if (cart[index]) {
            cart[index].quantity = (cart[index].quantity || 1) + delta;
            if (cart[index].quantity <= 0) {
                cart.splice(index, 1);
            }
            saveCart(cart);
        }
    };

    window.removeFromCart = function(index) {
        let cart = getCart();
        cart.splice(index, 1);
        saveCart(cart);
    };

    function openCart() {
        if (cartModal) {
            renderCartDrawer();
            cartModal.classList.remove("hidden");
        }
    }

    function closeCart() {
        if (cartModal) {
            cartModal.classList.add("hidden");
        }
    }

    if (cartBtn) cartBtn.addEventListener("click", openCart);
    if (closeCartBtn) closeCartBtn.addEventListener("click", closeCart);
    if (cartBackdrop) cartBackdrop.addEventListener("click", closeCart);

    if (cartCheckoutBtn) {
        cartCheckoutBtn.addEventListener("click", () => {
            const cart = getCart();
            if (cart.length === 0) {
                alert("Your cart is empty! Please add items first.");
                return;
            }
            window.location.href = "/checkout/";
        });
    }

    // Increase Quantity
    if (plusBtn) {
        plusBtn.addEventListener("click", () => {
            if (quantity < 10) {
                quantity++;
                if (quantityElement) quantityElement.textContent = quantity;
                updateDisplayPrice();
            }
        });
    }

    // Decrease Quantity
    if (minusBtn) {
        minusBtn.addEventListener("click", () => {
            if (quantity > 1) {
                quantity--;
                if (quantityElement) quantityElement.textContent = quantity;
                updateDisplayPrice();
            }
        });
    }

    // Add Product To Cart
    function addProductToCart() {
        let cart = getCart();
        const productName = document.querySelector(".heading-font.text-2xl, .heading-font.text-3xl")?.textContent?.trim() || "Premium Hair Growth Oil";

        const existingProduct = cart.find(
            item => item.name === productName
        );

        if (existingProduct) {
            existingProduct.quantity += quantity;
        } else {
            cart.push({
                name: productName,
                price: unitPrice,
                quantity: quantity
            });
        }

        saveCart(cart);
        showToast();
    }

    // Toast
    function showToast() {
        if (!toastText || !cartToast) return;
        toastText.textContent = `${quantity} ${quantity === 1 ? "item" : "items"} added to cart`;
        cartToast.classList.remove("translate-y-24", "opacity-0");
        cartToast.classList.add("translate-y-0", "opacity-100");

        setTimeout(() => {
            cartToast.classList.remove("translate-y-0", "opacity-100");
            cartToast.classList.add("translate-y-24", "opacity-0");
        }, 2500);
    }

    // Variant Quantity Handler
    window.changeVariantQty = function(spanId, delta) {
        const el = document.getElementById(spanId);
        if (!el) return;
        let currentQty = parseInt(el.textContent) || 1;
        currentQty += delta;
        if (currentQty < 1) currentQty = 1;
        if (currentQty > 10) currentQty = 10;
        el.textContent = currentQty;
    };

    // Variant Add To Cart Handler
    window.addVariantToCart = function(productName, price, spanId, isBuyNow = false) {
        const el = document.getElementById(spanId);
        const qty = el ? (parseInt(el.textContent) || 1) : 1;
        let cart = getCart();

        const existingIndex = cart.findIndex(item => item.name === productName);
        if (existingIndex > -1) {
            cart[existingIndex].quantity = (cart[existingIndex].quantity || 1) + qty;
        } else {
            cart.push({
                name: productName,
                price: parseFloat(price),
                quantity: qty
            });
        }

        saveCart(cart);

        if (isBuyNow) {
            // Buy Now: seedha checkout pe le jao
            window.location.href = "/checkout/";
        } else {
            // Add to Cart: toast dikhao
            if (toastText && cartToast) {
                toastText.textContent = `${qty}x ${productName} cart mein add ho gaya!`;
                cartToast.classList.remove("translate-y-24", "opacity-0");
                cartToast.classList.add("translate-y-0", "opacity-100");

                setTimeout(() => {
                    cartToast.classList.remove("translate-y-0", "opacity-100");
                    cartToast.classList.add("translate-y-24", "opacity-0");
                }, 2500);
            }
        }
    };

    // Initial updates on load
    updateCartBadge();
    renderCartDrawer();

// ====================================

    const reviewTrack = document.getElementById("reviewTrack");
    const reviewSlides = document.querySelectorAll(".review-slide");
    const reviewPrev = document.getElementById("reviewPrev");
    const reviewNext = document.getElementById("reviewNext");
    const reviewDots = document.getElementById("reviewDots");

    let reviewIndex = 0;


    // Get number of visible cards
    function getVisibleReviews() {

        if (window.innerWidth >= 1024) {
            return 3;
        }

        if (window.innerWidth >= 768) {
            return 2;
        }

        return 1;
    }


    // Calculate maximum slide index
    function getMaxIndex() {

        return Math.max(
            0,
            reviewSlides.length - getVisibleReviews()
        );

    }


    // Create dots
    function createReviewDots() {

        reviewDots.innerHTML = "";

        const totalDots = getMaxIndex() + 1;

        for (let i = 0; i < totalDots; i++) {

            const dot = document.createElement("button");

            dot.className =
                "w-2.5 h-2.5 rounded-full bg-gray-300 transition-all duration-300";

            dot.setAttribute(
                "aria-label",
                `Go to review group ${i + 1}`
            );

            dot.addEventListener("click", () => {

                reviewIndex = i;

                updateReviews();

            });

            reviewDots.appendChild(dot);

        }

    }


    // Update slider
    function updateReviews() {

        const visible = getVisibleReviews();

        const movePercentage = 100 / visible;

        reviewTrack.style.transform =
            `translateX(-${reviewIndex * movePercentage}%)`;


        // Update dots
        const dots = reviewDots.querySelectorAll("button");

        dots.forEach((dot, index) => {

            if (index === reviewIndex) {

                dot.classList.remove("bg-gray-300");

                dot.classList.add(
                    "bg-green-700",
                    "w-7"
                );

            } else {

                dot.classList.remove(
                    "bg-green-700",
                    "w-7"
                );

                dot.classList.add(
                    "bg-gray-300",
                    "w-2.5"
                );

            }

        });

    }


    // Next
    if (reviewNext) {
        reviewNext.addEventListener("click", () => {
            const maxIndex = getMaxIndex();
            if (reviewIndex < maxIndex) {
                reviewIndex++;
            } else {
                reviewIndex = 0;
            }
            updateReviews();
        });
    }

    // Previous
    if (reviewPrev) {
        reviewPrev.addEventListener("click", () => {
            const maxIndex = getMaxIndex();
            if (reviewIndex > 0) {
                reviewIndex--;
            } else {
                reviewIndex = maxIndex;
            }
            updateReviews();
        });
    }


    // Resize
    window.addEventListener("resize", () => {

        const maxIndex = getMaxIndex();

        if (reviewIndex > maxIndex) {
            reviewIndex = maxIndex;
        }

        createReviewDots();
        updateReviews();

    });


    // Initialize
    createReviewDots();
    updateReviews();


    // ================= FAQ ACCORDION =================

const faqQuestions = document.querySelectorAll(".faq-question");

faqQuestions.forEach((question) => {

    question.addEventListener("click", () => {

        const currentAnswer =
            question.nextElementSibling;

        const currentIcon =
            question.querySelector(".faq-icon");


        // Check if current FAQ is already open
        const isOpen =
            currentAnswer.style.maxHeight;


        // Close all FAQs
        document.querySelectorAll(".faq-answer").forEach((answer) => {

            answer.style.maxHeight = null;

        });


        document.querySelectorAll(".faq-icon").forEach((icon) => {

            icon.textContent = "+";
            icon.classList.remove("rotate-45");

        });


        // Open clicked FAQ
        if (!isOpen) {

            currentAnswer.style.maxHeight =
                currentAnswer.scrollHeight + "px";

            currentIcon.textContent = "+";

            currentIcon.classList.add("rotate-45");

        }

    });

});

// ================= LOGIN MODAL LOGIC =================
document.addEventListener("DOMContentLoaded", () => {
    const userLoginBtn = document.getElementById("userLoginBtn");
    const mobileLoginBtn = document.getElementById("mobileLoginBtn");
    const loginModal = document.getElementById("loginModal");
    const loginModalContainer = document.getElementById("loginModalContainer");
    const closeLoginModalBtn = document.getElementById("closeLoginModalBtn");
    const signInTab = document.getElementById("signInTab");
    const signUpTab = document.getElementById("signUpTab");
    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");
    const authAlert = document.getElementById("authAlert");

    function openLoginModal() {
        if (!loginModal) return;
        loginModal.classList.remove("opacity-0", "pointer-events-none");
        loginModal.classList.add("opacity-100");
        if (loginModalContainer) {
            loginModalContainer.classList.remove("scale-95");
            loginModalContainer.classList.add("scale-100");
        }
    }

    function closeLoginModal() {
        if (!loginModal) return;
        loginModal.classList.remove("opacity-100");
        loginModal.classList.add("opacity-0", "pointer-events-none");
        if (loginModalContainer) {
            loginModalContainer.classList.remove("scale-100");
            loginModalContainer.classList.add("scale-95");
        }
    }

    if (userLoginBtn) userLoginBtn.addEventListener("click", openLoginModal);
    if (mobileLoginBtn) mobileLoginBtn.addEventListener("click", openLoginModal);
    if (closeLoginModalBtn) closeLoginModalBtn.addEventListener("click", closeLoginModal);
    if (loginModal) {
        loginModal.addEventListener("click", (e) => {
            if (e.target === loginModal) closeLoginModal();
        });
    }

    // Tabs
    if (signInTab && signUpTab) {
        signInTab.addEventListener("click", () => {
            signInTab.classList.add("text-green-700", "border-b-2", "border-green-600", "font-bold");
            signInTab.classList.remove("text-gray-400", "font-medium");
            signUpTab.classList.remove("text-green-700", "border-b-2", "border-green-600", "font-bold");
            signUpTab.classList.add("text-gray-400", "font-medium");

            if (signInForm) signInForm.classList.remove("hidden");
            if (signUpForm) signUpForm.classList.add("hidden");
            if (authAlert) authAlert.classList.add("hidden");
        });

        signUpTab.addEventListener("click", () => {
            signUpTab.classList.add("text-green-700", "border-b-2", "border-green-600", "font-bold");
            signUpTab.classList.remove("text-gray-400", "font-medium");
            signInTab.classList.remove("text-green-700", "border-b-2", "border-green-600", "font-bold");
            signInTab.classList.add("text-gray-400", "font-medium");

            if (signUpForm) signUpForm.classList.remove("hidden");
            if (signInForm) signInForm.classList.add("hidden");
            if (authAlert) authAlert.classList.add("hidden");
        });
    }

    // Form Submissions
    function handleAuthSubmit(form, url) {
        if (!form) return;
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (authAlert) {
                authAlert.classList.add("hidden");
            }
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": data.csrfmiddlewaretoken || ""
                    },
                    body: JSON.stringify(data)
                });
                const result = await response.json();

                if (response.ok && result.success) {
                    if (authAlert) {
                        authAlert.className = "mb-4 p-3.5 rounded-2xl text-xs font-semibold bg-green-50 text-green-700 border border-green-200 block flex items-center gap-2";
                        authAlert.textContent = result.message || "Success!";
                    }
                    setTimeout(() => {
                        window.location.reload();
                    }, 800);
                } else {
                    if (authAlert) {
                        authAlert.className = "mb-4 p-3.5 rounded-2xl text-xs font-semibold bg-red-50 text-red-600 border border-red-200 block flex items-center gap-2";
                        authAlert.textContent = result.message || "An error occurred.";
                    }
                }
            } catch (err) {
                if (authAlert) {
                    authAlert.className = "mb-4 p-3.5 rounded-2xl text-xs font-semibold bg-red-50 text-red-600 border border-red-200 block flex items-center gap-2";
                    authAlert.textContent = "Something went wrong. Please try again.";
                }
            }
        });
    }

    handleAuthSubmit(signInForm, "/login/");
    handleAuthSubmit(signUpForm, "/register/");
});
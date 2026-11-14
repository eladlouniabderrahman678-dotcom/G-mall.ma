import os
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gmall_customer_first_2026'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قائمة المنتجات الافتراضية
PRODUCTS = [
    {
        "id": 1, 
        "name": "Montre connectée étanche - Smart Watch Pro", 
        "price": 450, 
        "old_price": 600,
        "sold": "2,000+ vendus",
        "rating": "★ 4.9",
        "tag": "Nouveaux clients",
        "location": "Entrepôt principal - Étagère A1",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "description": "Montre connectée originale de haute qualité, prend en charge la fréquence cardiaque et le suivi du fitness."
    },
    {
        "id": 2, 
        "name": "Mini vitrine d'exposition LED - G-Mall", 
        "price": 300, 
        "old_price": 420,
        "sold": "1,000+ vendus",
        "rating": "★ 4.7",
        "tag": "SuperDeals",
        "location": "Entrepôt secondaire - Étagère B2",
        "image": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=500",
        "description": "Boîte de présentation détaillée avec éclairage LED intérieur pour les collectionneurs."
    }
]

HOME_HTML = """
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G-Mall | Boutique Intelligente</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, sans-serif; }
        body { background-color: #f3f3f3; color: #222; padding-bottom: 70px; direction: ltr; text-align: left; }

        .top-header { background: #ffffff; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e5e5e5; position: sticky; top: 0; z-index: 100; }
        .logo { font-weight: bold; font-size: 20px; color: #2563eb; }
        .cart-icon-btn { background: #2563eb; color: white; padding: 6px 14px; border-radius: 20px; text-decoration: none; font-size: 14px; font-weight: bold; }
        .cart-badge { background: #1e3a8a; color: white; border-radius: 50%; padding: 2px 6px; font-size: 11px; margin-left: 5px; }
        .admin-btn { background: #1e3a8a; color: white; border: none; padding: 6px 12px; border-radius: 15px; font-size: 12px; text-decoration: none; margin-right: 10px; }

        .container { padding: 15px; max-width: 1200px; margin: auto; }
        .section-title { font-size: 18px; font-weight: bold; margin: 15px 0 10px; color: #111; }

        .admin-panel { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #2563eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .admin-panel input, .admin-panel textarea { width: 100%; padding: 10px; margin: 6px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .btn-submit { background: #2563eb; color: white; border: none; padding: 10px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; margin-top: 5px; }

        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: space-between; }
        .product-card img { width: 100%; height: 170px; object-fit: cover; border-radius: 6px; }
        .product-name { font-size: 14px; color: #222; margin: 8px 0; height: 38px; overflow: hidden; }
        .price-now { color: #2563eb; font-size: 18px; font-weight: bold; }
        .price-old { color: #999; font-size: 12px; text-decoration: line-through; margin-right: 6px; }
        
        .btn-add-cart { background: #3b82f6; color: white; border: none; padding: 8px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; margin-top: 8px; font-size: 13px; }
        .btn-add-cart:hover { background: #1d4ed8; }

        .modal { display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; }
        .modal-content { background: white; padding: 25px; border-radius: 12px; width: 90%; max-width: 420px; box-shadow: 0 5px 20px rgba(0,0,0,0.3); }
        .modal-content h3 { color: #2563eb; margin-bottom: 8px; font-size: 18px; }
        .modal-content input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .modal-btn { background: #25d366; color: white; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 12px; font-size: 15px; }
        .close-modal { background: #e0e0e0; color: #333; margin-top: 6px; }
    </style>
</head>
<body>

    <div class="top-header">
        <div class="logo">🛒 G-MALL Maroc</div>
        <div>
            <a href="/cart" class="cart-icon-btn">
                <span>Panier</span>
                <span class="cart-badge" id="cart-count">0</span>
            </a>
            {% if logged_in %}
                <a href="/logout" class="admin-btn">Déconnexion</a>
            {% else %}
                <a href="/login" class="admin-btn">Admin</a>
            {% endif %}
        </div>
    </div>

    <div class="container">
        {% if logged_in %}
        <div class="admin-panel">
            <h3>➕ Ajouter un nouveau produit</h3>
            <form action="/add" method="POST" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="Nom du produit" required>
                <input type="number" step="0.01" name="price" placeholder="Prix actuel (MAD)" required>
                <input type="number" step="0.01" name="old_price" placeholder="Ancien prix (barré)" required>
                <input type="file" name="image_file" accept="image/*" required>
                <input type="text" name="location" placeholder="Emplacement (ex: Fès)" required>
                <textarea name="description" placeholder="Description du produit..." rows="2"></textarea>
                <button type="submit" class="btn-submit">Publier le produit</button>
            </form>
        </div>
        {% endif %}

        <div class="section-title">⚡ Offres disponibles actuellement</div>

        <div class="products-grid">
            {% for p in products %}
            <div class="product-card">
                <div>
                    <a href="/product/{{ p.id }}" style="text-decoration:none; color:inherit;">
                        <img src="{{ p.image }}" alt="{{ p.name }}">
                        <div class="product-name">{{ p.name }}</div>
                        <div>
                            <span class="price-now">{{ p.price }} DH</span>
                            <span class="price-old">{{ p.old_price }} DH</span>
                        </div>
                    </a>
                </div>
                <button type="button" class="btn-add-cart" onclick="openCustomerModal('{{ p.name }}', {{ p.price }})">Ajouter au panier 🛒</button>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- النافذة المنبثقة لإدخال المعلومات -->
    <div id="customerModal" class="modal">
        <div class="modal-content">
            <h3>📝 Saisissez vos coordonnées</h3>
            <p style="font-size: 13px; color: #666; margin-bottom: 12px;">Veuillez remplir vos informations pour continuer l'achat :</p>
            <input type="text" id="m-name" placeholder="Nom complet" required>
            <input type="text" id="m-phone" placeholder="Numéro de téléphone (ex: 06...)" required>
            <input type="email" id="m-email" placeholder="Adresse e-mail (Gmail)" required>
            <input type="text" id="m-address" placeholder="Adresse détaillée (Ville / Quartier)" required>
            
            <button type="button" class="modal-btn" onclick="saveCustomerAndAddToCart()">Enregistrer et ajouter au panier ✅</button>
            <button type="button" class="modal-btn close-modal" onclick="closeCustomerModal()">Annuler ❌</button>
        </div>
    </div>

    <script>
        let pendingProduct = null;

        function openCustomerModal(name, price) {
            let savedInfo = localStorage.getItem('gmall_customer');
            pendingProduct = {name: name, price: price};

            if (savedInfo) {
                finalizeAddToCart(pendingProduct.name, pendingProduct.price);
            } else {
                document.getElementById('customerModal').style.display = 'flex';
            }
        }

        function closeCustomerModal() {
            document.getElementById('customerModal').style.display = 'none';
            pendingProduct = null;
        }

        function saveCustomerAndAddToCart() {
            let name = document.getElementById('m-name').value.trim();
            let phone = document.getElementById('m-phone').value.trim();
            let email = document.getElementById('m-email').value.trim();
            let address = document.getElementById('m-address').value.trim();

            if (!name || !phone || !email || !address) {
                alert("Veuillez remplir tous les champs obligatoires !");
                return;
            }

            let customerInfo = {name: name, phone: phone, email: email, address: address};
            localStorage.setItem('gmall_customer', JSON.stringify(customerInfo));

            closeCustomerModal();
            
            if (pendingProduct) {
                finalizeAddToCart(pendingProduct.name, pendingProduct.price);
            }
        }

        function finalizeAddToCart(name, price) {
            let cart = JSON.parse(localStorage.getItem('gmall_cart')) || [];
            cart.push({name: name, price: price});
            localStorage.setItem('gmall_cart', JSON.stringify(cart));
            updateCartCount();
            alert("Produit ajouté au panier avec succès ! ✅");
        }

        function updateCartCount() {
            let cart = JSON.parse(localStorage.getItem('gmall_cart')) || [];
            document.getElementById('cart-count').innerText = cart.length;
        }

        updateCartCount();
    </script>
</body>
</html>
"""

DETAIL_HTML = """
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
    <meta charset="UTF-8">
    <title>{{ product.name }} - Détails du produit</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, sans-serif; }
        body { background: #f3f3f3; margin: 0; padding: 20px; direction: ltr; text-align: left; }
        .container { max-width: 600px; margin: auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        img { width: 100%; height: 300px; object-fit: contain; background: #000; border-radius: 6px; }
        .title { font-size: 20px; font-weight: bold; margin: 15px 0 10px; }
        .price { font-size: 24px; color: #2563eb; font-weight: bold; margin-bottom: 15px; }
        .btn { display: block; width: 100%; padding: 12px; text-align: center; border-radius: 5px; font-weight: bold; text-decoration: none; margin-top: 10px; cursor: pointer; border: none; font-size: 15px; }
        .btn-cart { background: #3b82f6; color: white; }
        .btn-cart:hover { background: #1d4ed8; }
        .btn-back { background: #1e3a8a; color: white; }

        .modal { display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; }
        .modal-content { background: white; padding: 25px; border-radius: 12px; width: 90%; max-width: 420px; box-shadow: 0 5px 20px rgba(0,0,0,0.3); }
        .modal-content h3 { color: #2563eb; margin-bottom: 8px; font-size: 18px; }
        .modal-content input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .modal-btn { background: #25d366; color: white; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 6px; cursor: pointer; margin-top: 12px; font-size: 15px; }
        .close-modal { background: #e0e0e0; color: #333; margin-top: 6px; }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ product.image }}" alt="{{ product.name }}">
        <div class="title">{{ product.name }}</div>
        <div class="price">{{ product.price }} DH <span style="font-size:14px; color:#888; text-decoration:line-through; margin-left: 6px;">{{ product.old_price }} DH</span></div>
        <p><strong>📍 Emplacement :</strong> {{ product.location }}</p>
        <p><strong>Description :</strong> {{ product.description }}</p>
        
        <button type="button" class="btn btn-cart" onclick="openCustomerModal('{{ product.name }}', {{ product.price }})">Ajouter au panier 🛒</button>
        <a href="/" class="btn btn-back">Retour à la boutique</a>
    </div>

    <!-- النافذة المنبثقة لإدخال المعلومات في صفحة التفاصيل -->
    <div id="customerModal" class="modal">
        <div class="modal-content">
            <h3>📝 Saisissez vos coordonnées</h3>
            <p style="font-size: 13px; color: #666; margin-bottom: 12px;">Veuillez remplir vos informations pour continuer l'achat :</p>
            <input type="text" id="m-name" placeholder="Nom complet" required>
            <input type="text" id="m-phone" placeholder="Numéro de téléphone (ex: 06...)" required>
            <input type="email" id="m-email" placeholder="Adresse e-mail (Gmail)" required>
            <input type="text" id="m-address" placeholder="Adresse détaillée (Ville / Quartier)" required>
            
            <button type="button" class="modal-btn" onclick="saveCustomerAndAddToCart()">Enregistrer et ajouter au panier ✅</button>
            <button type="button" class="modal-btn close-modal" onclick="closeCustomerModal()">Annuler ❌</button>
        </div>
    </div>

    <script>
        let pendingProduct = null;

        function openCustomerModal(name, price) {
            let savedInfo = localStorage.getItem('gmall_customer');
            pendingProduct = {name: name, price: price};

            if (savedInfo) {
                finalizeAddToCart(pendingProduct.name, pendingProduct.price);
            } else {
                document.getElementById('customerModal').style.display = 'flex';
            }
        }

        function closeCustomerModal() {
            document.getElementById('customerModal').style.display = 'none';
            pendingProduct = null;
        }

        function saveCustomerAndAddToCart() {
            let name = document.getElementById('m-name').value.trim();
            let phone = document.getElementById('m-phone').value.trim();
            let email = document.getElementById('m-email').value.trim();
            let address = document.getElementById('m-address').value.trim();

            if (!name || !phone || !email || !address) {
                alert("Veuillez remplir tous les champs obligatoires !");
                return;
            }

            let customerInfo = {name: name, phone: phone, email: email, address: address};
            localStorage.setItem('gmall_customer', JSON.stringify(customerInfo));

            closeCustomerModal();
            
            if (pendingProduct) {
                finalizeAddToCart(pendingProduct.name, pendingProduct.price);
            }
        }

        function finalizeAddToCart(name, price) {
            let cart = JSON.parse(localStorage.getItem('gmall_cart')) || [];
            cart.push({name: name, price: price});
            localStorage.setItem('gmall_cart', JSON.stringify(cart));
            alert("Produit ajouté au panier avec succès ! ✅");
        }
    </script>
</body>
</html>
"""

CART_HTML = """
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
    <meta charset="UTF-8">
    <title>Panier et Finalisation de Commande</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, sans-serif; }
        body { background: #f3f3f3; margin: 0; padding: 20px; direction: ltr; text-align: left; }
        .container { max-width: 600px; margin: auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { color: #2563eb; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .item-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 15px; }
        .total-box { font-size: 18px; font-weight: bold; text-align: right; margin: 15px 0; color: #222; }
        .customer-info-box { background: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 14px; border: 1px solid #ddd; }
        .btn-whatsapp { background: #25d366; color: white; border: none; width: 100%; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 5px; cursor: pointer; margin-top: 15px; }
        .btn-back { display: block; text-align: center; margin-top: 10px; color: #666; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛒 Votre Panier d'Achats</h2>
        
        <div class="customer-info-box" id="cust-display"></div>

        <div id="cart-items"></div>
        <div class="total-box" id="cart-total">Total : 0 DH</div>

        <button type="button" class="btn-whatsapp" onclick="sendOrder()">Confirmer et envoyer la commande via WhatsApp 📱</button>
        <a href="/" class="btn-back">← Continuer vos achats</a>
    </div>

    <script>
        function loadCartData() {
            let cart = JSON.parse(localStorage.getItem('gmall_cart')) || [];
            let customer = JSON.parse(localStorage.getItem('gmall_customer'));
            let container = document.getElementById('cart-items');
            let totalBox = document.getElementById('cart-total');
            let custDisplay = document.getElementById('cust-display');
            
            if (customer) {
                custDisplay.innerHTML = `
                    <b>👤 Nom :</b> ${customer.name} <br>
                    <b>📞 Téléphone :</b> ${customer.phone} <br>
                    <b>📧 Email :</b> ${customer.email} <br>
                    <b>📍 Adresse :</b> ${customer.address}
                `;
            } else {
                custDisplay.innerHTML = "<span style='color:red;'>Vous n'avez pas encore saisi vos informations ! Veuillez ajouter un produit depuis la page d'accueil.</span>";
            }

            container.innerHTML = "";
            let total = 0;

            if (cart.length === 0) {
                container.innerHTML = "<p style='color:#777; text-align:center; padding:20px;'>Votre panier est vide.</p>";
                totalBox.innerText = "Total : 0 DH";
                return;
            }

            cart.forEach((item, index) => {
                total += parseFloat(item.price);
                container.innerHTML += `
                    <div class="item-row">
                        <span>${index + 1}. ${item.name}</span>
                        <span><b>${item.price} DH</b></span>
                    </div>
                `;
            });
            totalBox.innerText = `Total Général : ${total} DH`;
        }

        function sendOrder() {
            let cart = JSON.parse(localStorage.getItem('gmall_cart')) || [];
            let customer = JSON.parse(localStorage.getItem('gmall_customer'));

            if (!customer) {
                alert("Veuillez saisir vos informations personnelles d'abord !");
                window.location.href = "/";
                return;
            }

            if (cart.length === 0) {
                alert("Votre panier est vide ! Ajoutez des produits d'abord.");
                return;
            }

            let message = *Nouvelle commande de G-Mall* 🛒%0A%0A;
            message += *Nom :* ${customer.name}%0A;
            message += *Téléphone :* ${customer.phone}%0A;
            message += *Email :* ${customer.email}%0A;
            message += *Adresse :* ${customer.address}%0A%0A;
            message += *Produits demandés :*%0A;

            let total = 0;
            cart.forEach((item) => {
                message += - ${item.name} (${item.price} DH)%0A;
                total += parseFloat(item.price);
            });
            message += %0A*Total Général :* ${total} DH;

            let vendorPhone = "212632502148";
            let whatsappUrl = `https://wa.me/${vendorPhone}?text=${message}`;
            
            localStorage.removeItem('gmall_cart');
            window.location.href = whatsappUrl;
        }

        loadCartData();
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head><meta charset="UTF-8"><title>Connexion Admin</title></head>
<body style="font-family:Tahoma; display:flex; justify-content:center; align-items:center; height:100vh; background:#f3f3f3; direction: ltr;">
    <form method="POST" style="background:white; padding:30px; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1); text-align:center; width:300px;">
        <h3 style="color:#2563eb; margin-bottom:15px;">Espace Administrateur</h3>
        <input type="password" name="password" placeholder="Mot de passe (1234)" required style="padding:10px; width:100%; border:1px solid #ccc; border-radius:4px; margin-bottom:15px;">
        <button type="submit" style="padding:10px; width:100%; background:#2563eb; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Connexion</button>
    </form>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML, products=PRODUCTS, logged_in=session.get('logged_in'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return "Produit introuvable !", 404
    return render_template_string(DETAIL_HTML, product=product)

@app.route('/cart')
def cart_page():
    return render_template_string(CART_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == '1234':
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = float(request.form.get('price'))
    old_price = float(request.form.get('old_price'))
    location = request.form.get('location')
    description = request.form.get('description')
    
    image_url = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
    file = request.files.get('image_file')
    if file and file.filename != '':
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        image_url = f"/{UPLOAD_FOLDER}/{file.filename}"

    PRODUCTS.append({
        "id": len(PRODUCTS) + 1,
        "name": name,
        "price": price,
        "old_price": old_price,
        "sold": "Nouveau",
        "rating": "★ 5.0",
        "tag": "Offre spéciale",
        "location": location,
        "image": image_url,
        "description": description
    })
    return redirect(url_for('home'))

if __name__ == '__main__':
  app.run(debug=True)  

from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(_name_)
app.secret_key = 'votre_cle_secrete'  # ضروري لتفعيل الـ Sessions

@app.route('/cart')
def view_cart():
    # جلب السلة ومعلومات الزبون من الـ Session في بايثون
    cart = session.get('cart', [])
    customer = session.get('customer', {})
    
    # حساب المجموع الإجمالي في بايثون
    total = 0
    for item in cart:
        item_price = float(item.get('price', 0))
        total += item_price
        
    return render_template('cart.html', cart=cart, customer=customer, total=total)
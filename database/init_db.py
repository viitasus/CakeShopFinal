from app import create_app
from database.models import db, User, Category, Product
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with some sample data"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if there's already data
        if User.query.first() is not None:
            print("Database already has data, skipping initialization")
            return
        
        print("Initializing database with sample data...")
        
        # Create admin user
        admin = User(
            email="admin@happycake.com",
            password_hash=generate_password_hash("Admin@123"),
            name="Admin User",
            phone="1234567890",
            is_admin=True
        )
        db.session.add(admin)
        
        # Create categories
        categories = [
            Category(name="Birthday Cakes", slug="birthday", description="Delicious cakes for birthday celebrations"),
            Category(name="Wedding Cakes", slug="wedding", description="Elegant cakes for wedding ceremonies"),
            Category(name="Seasonal Cakes", slug="seasonal", description="Special cakes for seasonal festivities"),
            Category(name="Custom Cakes", slug="custom", description="Unique cakes customized to your preferences")
        ]
        
        for category in categories:
            db.session.add(category)
        
        # Commit to get category IDs
        db.session.commit()
        
        # Get categories for products
        birthday_category = Category.query.filter_by(slug="birthday").first()
        wedding_category = Category.query.filter_by(slug="wedding").first()
        seasonal_category = Category.query.filter_by(slug="seasonal").first()
        custom_category = Category.query.filter_by(slug="custom").first()
        
        # Create products
        products = [
            Product(
                name="Chocolate Truffle Cake",
                slug="chocolate-truffle",
                description="Rich chocolate cake with truffle cream and chocolate ganache.",
                price=799,
                is_available=True
            ),
            Product(
                name="Vanilla Bliss Cake",
                slug="vanilla-bliss",
                description="Fluffy vanilla sponge with vanilla cream and white chocolate.",
                price=649,
                is_available=True
            ),
            Product(
                name="Strawberry Delight Cake",
                slug="strawberry-delight",
                description="Soft vanilla cake with strawberry filling and whipped cream.",
                price=749,
                is_available=True
            ),
            Product(
                name="Black Forest Cake",
                slug="black-forest",
                description="Chocolate cake with cherry filling and whipped cream.",
                price=699,
                is_available=True
            ),
            Product(
                name="Mango Tango Cake",
                slug="mango-tango",
                description="Mango flavored cake with fresh mango pieces and cream.",
                price=849,
                is_available=True
            ),
            Product(
                name="Butterscotch Symphony Cake",
                slug="butterscotch-symphony",
                description="Butterscotch cake with caramel drizzle and nuts.",
                price=699,
                is_available=True
            ),
            Product(
                name="Red Velvet Love Cake",
                slug="red-velvet-love",
                description="Classic red velvet cake with cream cheese frosting.",
                price=849,
                is_available=True
            ),
            Product(
                name="Pineapple Paradise Cake",
                slug="pineapple-paradise",
                description="Pineapple flavored cake with pineapple chunks and cream.",
                price=699,
                is_available=True
            ),
            Product(
                name="Elegant Wedding Cake",
                slug="elegant-wedding",
                description="Three-tier wedding cake with elegant decorations.",
                price=5999,
                is_available=True
            ),
            Product(
                name="Christmas Special Cake",
                slug="christmas-special",
                description="Festive cake with Christmas themed decorations.",
                price=999,
                is_available=True
            ),
            Product(
                name="Rainbow Cake",
                slug="rainbow",
                description="Colorful layered cake with rainbow colors inside.",
                price=899,
                is_available=True
            ),
            Product(
                name="Custom Photo Cake",
                slug="custom-photo",
                description="Cake with your custom photo printed on top.",
                price=1099,
                is_available=True
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        # Commit to get product IDs
        db.session.commit()
        
        # Assign categories to products
        products[0].categories.append(birthday_category)  # Chocolate Truffle
        products[1].categories.append(birthday_category)  # Vanilla Bliss
        products[2].categories.append(birthday_category)  # Strawberry Delight
        products[3].categories.append(birthday_category)  # Black Forest
        products[4].categories.append(seasonal_category)  # Mango Tango
        products[5].categories.append(birthday_category)  # Butterscotch
        products[6].categories.append(birthday_category)  # Red Velvet
        products[6].categories.append(wedding_category)   # Red Velvet also for weddings
        products[7].categories.append(birthday_category)  # Pineapple
        products[8].categories.append(wedding_category)   # Elegant Wedding
        products[9].categories.append(seasonal_category)  # Christmas
        products[10].categories.append(birthday_category) # Rainbow
        products[11].categories.append(custom_category)   # Custom Photo
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
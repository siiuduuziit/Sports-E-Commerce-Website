from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tags(models.Model):
    pass


STATUS_CHOICES = (
    ('ordered', 'Đã Đặt Hàng'),
    # ('preorder', 'Đặt Trước'),
    # ('delivered', 'Đã Giao Hàng'),
    ('canceled', 'Đã Hủy'),
    ('returned', 'Đã Trả Hàng'),
    ('done', 'Hoàn Thành'),
)

STATUS = (
    ('draft', 'Bản Nháp'),
    ('disabled', 'Vô Hiệu Hóa'),
    ('available', 'Có Hàng'),
)

RATING_CHOICES = (
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
)

PAYMENT_METHOD_CHOICES = (
    ('cod', 'Thanh toán khi nhận hàng'),
    ('bank', 'Chuyển khoản ngân hàng'),
)


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat_", alphabet="abcdefghijklmnopqrstuvwxyz0123456789")

    ctitle = models.CharField(max_length=100, default="Tên Danh Mục")
    cimage = models.ImageField(upload_to='category_images/', default='default_category.png')

    class Meta:
        verbose_name_plural = "Categories"

    
    def category_image(self):
        return mark_safe(f'<img src="{self.cimage.url}" width="50" height="50" />')
    

    def __str__(self):
        return self.ctitle
    

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=10, prefix="ven_", alphabet="abcdefghijklmnopqrstuvwxyz0123456789")
    
    title = models.CharField(max_length=100, default="Tên Nhà Cung Cấp")
    image = models.ImageField(upload_to=user_directory_path, default='default_vendor.png')
    description = RichTextUploadingField(null=True, blank=True, default="Không có mục miêu tả.")
    
    address = models.CharField(max_length=100, default='123 Đường A', null=True, blank=True)
    contact_number = models.CharField(max_length=15, default='+84 123 4567', null=True, blank=True)
    chat_response_time = models.CharField(max_length=50, default='9 AM - 6 PM', null=True, blank=True)
    shipping_time = models.CharField(max_length=50, default='3-5 Ngày làm việc', null=True, blank=True)
    authentic_rating = models.CharField(max_length=50, default='99% Hàng chính hãng', null=True, blank=True)
    warranty_policy = models.CharField(max_length=100, default='Bảo hành 12 tháng', null=True, blank=True)
    days_return_policy = models.CharField(max_length=50, default='Đổi trả trong 7 ngày', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


    class Meta:
        verbose_name_plural = "Vendors"

    
    def vendor_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
    

    def __str__(self):
        return self.title
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="pro_", alphabet="abcdefghijklmnopqrstuvwxyz0123456789")
    
    title = models.CharField(max_length=200, default="Tên Sản Phẩm")
    image = models.ImageField(upload_to=user_directory_path, default='default_product.png')
    description = RichTextUploadingField(null=True, blank=True, default="Không có mục miêu tả.")
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=0, default=0, null=True, blank=True)
    get_percentage = models.DecimalField(max_digits=10, decimal_places=0, default=0, null=True, blank=True)
    specifications = RichTextUploadingField(null=True, blank=True, default="Không có mục thông số kỹ thuật.")
    product_status = models.CharField(choices=STATUS, max_length=20, default='disabled')
    stock = models.PositiveIntegerField(default=0)

    # status = models.BooleanField(default=True)
    # in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    # digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=8, max_length=20, prefix="sku_", alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)


    class Meta:
        verbose_name_plural = "Products"


    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
    

    def __str__(self):
        return self.title
    

    def get_percent_discount(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
    

    def get_absolute_url(self):
        return reverse('core:product-details', args=[self.pid])
    
    
    @property
    def get_percentage(self):
        if self.old_price and self.price and self.old_price > self.price:
            return ((self.old_price - self.price) / self.old_price) * 100
        return 0
    

class ProductGallery(models.Model):
    images = models.ImageField(upload_to='product_images/', default='default_product.png')
    product = models.ForeignKey(Product, related_name='p_images', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Galleries"


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='Đã Đặt Hàng')
    full_name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    province_name = models.CharField(max_length=255, null=True)
    district_name = models.CharField(max_length=255, null=True)
    ward_name = models.CharField(max_length=255, null=True)
    address_line = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True, blank=True)
    saved = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    coupons = models.ManyToManyField('core.Coupon', blank=True)
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )


    class Meta:
        verbose_name_plural = "Cart Orders"


class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    product_status = models.CharField(max_length=100)
    item = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    invoice = models.CharField(max_length=100)


    class Meta:
        verbose_name_plural = "Cart Order Items"


    def order_image(self):
        return mark_safe(f'<img src="/media/{self.image}" width="50" height="50" />')
    

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField(null=True, blank=True)
    rating = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Reviews"


    # def __str__(self):
    #     return f"Review by {self.user.username} for {self.product.title}"


    def __str__(self):
        return self.product.title
    

    def review_rating(self):
        return self.rating
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Wishlists"


    # def __str__(self):
    #     return f"{self.user.username}'s wishlist item: {self.product.title}"


    def __str__(self):
        return self.product.title
    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address_name = models.CharField(max_length=255, null=True)
    address_line = models.CharField(max_length=255, null=True)
    # city = models.CharField(max_length=100)
    # state = models.CharField(max_length=100)
    # postal_code = models.CharField(max_length=20)
    # country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True)
    # is_default = models.BooleanField(default=False)
    address_status = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = "Addresses"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    # Các thông tin khác như bio, avatar...


    def __str__(self):
        return self.user.username
    

    class Meta:
        verbose_name_plural = "Profile Points"


class Coupon(models.Model):
    coupon = models.CharField(max_length=10)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    points_required = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.coupon} (-{self.discount}%)"
    

    class Meta:
        verbose_name_plural = 'Coupons'


class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False) # Để đánh dấu nếu mã chỉ được dùng 1 lần


    def __str__(self):
        return f"{self.user.username} sở hữu {self.coupon.coupon}"
    

    class Meta:
        verbose_name_plural = "User Coupons"


class ChatbotFAQ(models.Model):
    keyword = models.CharField(max_length=100)
    answer = models.TextField()


    def __str__(self):
        return self.keyword
    

    class Meta:
        verbose_name_plural = 'ChatbotFAQ'


class ChatbotLog(models.Model):
    message = models.TextField()
    matched_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.message[:50]
    

    class Meta:
        verbose_name_plural = 'ChatbotLog'

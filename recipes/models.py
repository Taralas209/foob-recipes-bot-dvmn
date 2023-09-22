from django.db import models


class User(models.Model):
    telegram_id = models.PositiveIntegerField(verbose_name='Телеграм ID')
    start_subscription = models.DateField(verbose_name='Дата начала подписки')
    end_subscription = models.DateField(verbose_name='Дата окончания подписки')
    is_subscription = models.BooleanField(verbose_name='Активна ли подписка')
    category = models.ForeignKey('Category', related_name='users', verbose_name='Категория', on_delete=models.SET_NULL,
                                 null=True)

    def __str__(self):
        return self.telegram_id

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Recipes(models.Model):
    title = models.TextField(verbose_name='Название блюда')
    image = models.ImageField(verbose_name='Изображение блюда', upload_to='recipes')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    ingredients = models.ManyToManyField('Ingredients', verbose_name='Ингредиенты', related_name='Рецепты')
    category = models.ManyToManyField('Category', related_name='recipes', verbose_name='Категория')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Ingredients(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название', unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

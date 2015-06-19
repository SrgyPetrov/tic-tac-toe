from django.contrib import admin

from game.models import Game, Move


class MoveInlineAdmin(admin.StackedInline):

    model = Move


class GameAdmin(admin.ModelAdmin):

    inlines = [MoveInlineAdmin]


admin.site.register(Game, GameAdmin)

food_items = [food_item.strip() for food_item in food_list.split(',')]
        embed = discord.Embed(title="Food List", color=discord.Color.green())
        for i, item in enumerate(food_items, start=1):
            embed.add_field(name=f"{i}. {item}", value="", inline=False)
        view = gameclasses.ListMenu(user_manager, bot, food_items)
        await ctx.reply(embed=embed, view=view)
        await ctx.channel.send(responses.list_edit_message())
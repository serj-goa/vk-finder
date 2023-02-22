from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_keyboard(colors: tuple[tuple]) -> VkKeyboard:
    keyboard_colors = {
        'blue': VkKeyboardColor.PRIMARY,
        'white': VkKeyboardColor.SECONDARY,
        'green': VkKeyboardColor.POSITIVE,
        'red': VkKeyboardColor.NEGATIVE,
    }
    keyboard = VkKeyboard(one_time=True)

    for kbrd_label, kbrd_color in colors:
        keyboard.add_button(label=kbrd_label, color=keyboard_colors[kbrd_color])

    return keyboard

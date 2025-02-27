QUEUE = {}


def add_to_queue(chat_id, songname, link, ref, type, request, duration):
    if chat_id in QUEUE:
        chat_queue = QUEUE[chat_id]
        chat_queue.append([songname, link, ref, type, request, duration])
        return int(len(chat_queue) - 1)
    else:
        QUEUE[chat_id] = [[songname, link, ref, type, request, duration]]


def get_queue(chat_id):
    return QUEUE[chat_id] if chat_id in QUEUE else 0


def pop_an_item(chat_id):
    if chat_id not in QUEUE:
        return 0
    chat_queue = QUEUE[chat_id]
    chat_queue.pop(0)
    return 1


def clear_queue(chat_id):
    if chat_id not in QUEUE:
        return 0
    QUEUE.pop(chat_id)
    return 1

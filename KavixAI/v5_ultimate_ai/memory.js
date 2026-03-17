let memory = [];

function saveMemory(user, bot) {
    memory.push({ user, bot });
}

function findMemory(input) {
    return memory.find(m =>
        input.toLowerCase().includes(m.user.toLowerCase())
    );
}
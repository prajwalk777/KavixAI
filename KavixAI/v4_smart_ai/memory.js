// memory.js

let memory = [];

// Save memory
function saveMemory(user, bot) {
    memory.push({ user, bot });
}

// Get last memory
function getLastMemory() {
    return memory[memory.length - 1];
}

// Find similar memory
function findMemory(input) {
    return memory.find(m =>
        m.user.toLowerCase().includes(input.toLowerCase())
    );
}
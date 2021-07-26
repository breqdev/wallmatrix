let dropdown = document.getElementById("sources")

let messageInput = document.getElementById("message")
let flashButton = document.getElementById("flash")


async function fetchSources() {
    let data = await fetch("/sources")
    let sources = await data.json()

    let options = Object.entries(sources.all).map(([importName, friendlyName]) => {
        let option = document.createElement("option")
        option.value = importName
        option.innerHTML = friendlyName
        return option
    })

    dropdown.append(...options)
    dropdown.value = sources.current
}

fetchSources()

async function handleSourceChange() {
    let source = dropdown.value

    await fetch("/sources", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({source})
    })
}

dropdown.addEventListener("change", handleSourceChange)

async function handleFlashMessage() {
    let message = messageInput.value

    await fetch("/flash", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({message})
    })
}

flashButton.addEventListener("click", handleFlashMessage)

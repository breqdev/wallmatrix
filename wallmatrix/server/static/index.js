let dropdown = document.getElementById("sources")

async function fetch_sources() {
    let data = await fetch("/sources")
    let sources = await data.json()

    let options = Object.entries(sources.all).map(([importName, friendlyName]) => {
        let option = document.createElement("option")
        option.value = importName
        option.innerHTML = friendlyName
        return option
    })

    dropdown.replaceChildren(...options)
    dropdown.value = sources.current
}

fetch_sources()

async function handle_source_change() {
    let source = dropdown.value

    await fetch("/sources", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({source})
    })
}

dropdown.addEventListener("change", handle_source_change)
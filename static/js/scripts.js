function clickTopics() {
    let reviewButton = document.getElementById("reviewButton");
    let topicButton = document.getElementById("topicsButton");
    reviewButton.classList.remove("pure-menu-selected");
    topicButton.classList.add("pure-menu-selected");

    let reviewsDiv = document.getElementById("reviews");
    let topicsDiv = document.getElementById("topics");
    reviewsDiv.setAttribute("hidden", "true");
    topicsDiv.removeAttribute("hidden");
}

function clickReviews() {
    let reviewButton = document.getElementById("reviewButton");
    let topicButton = document.getElementById("topicsButton");
    topicButton.classList.remove("pure-menu-selected");
    reviewButton.classList.add("pure-menu-selected");
    let reviewsDiv = document.getElementById("reviews");
    let topicsDiv = document.getElementById("topics");
    reviewsDiv.removeAttribute("hidden");
    topicsDiv.setAttribute("hidden", "true");
}

function rate(value) {
    console.log(value);
    document.getElementById('rating').value = value;
    for (let i = 1; i <= 5; i++) {
        const star = document.getElementById('star' + i);
        if (i <= value) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    }
}

function editReply(commentId, originalContent, parent_id) {
    const commentContentElement = document.getElementById(`comment-content-${commentId}`);
    commentContentElement.innerHTML = `
        <form class = "pure-form" method="POST" action="/updateReply/${parent_id}/${commentId}">
            <textarea type="text" id="edit-comment-${commentId}" name="editArea"> ${originalContent} </textarea>
            <button class="pure-button pure-button-primary" onclick="cancelEdit(${commentId}, '${originalContent}')">Cancel</button>
            <input class="pure-button pure-button-primary" type="submit" id="submit" name="submit" value="save">
        </form>
    `;
}

function saveReply(commentId) {
    const editedContent = document.getElementById(`edit-comment-${commentId}`).value;
    // Here you would typically send the edited content to the server via an AJAX request.
    // For simplicity, we'll just update the content on the client side.
}

function cancelEdit(commentId, originalContent) {
    document.getElementById(`comment-content-${commentId}`).innerHTML = originalContent;
}

function clickGenre(genre) {
    let divNames = ['strategyDiv', 'rpgDiv', 'adventureDiv', 'fightingDiv', 'fpsDiv', 'platformDiv']
    let targetDiv = document.getElementById(genre + "Div")
    let targetButton = document.getElementById(genre + "Button")
    divNames.forEach(hideDiv)
    targetDiv.removeAttribute('hidden')
    targetButton.classList.add("pure-menu-selected");

}

function hideDiv(divName) {
    let divToHide = document.getElementById(divName)
    divToHide.setAttribute("hidden", "true");
    let buttonToRemove = document.getElementById(divName.replace('Div', 'Button'));
    buttonToRemove.classList.remove("pure-menu-selected");
}

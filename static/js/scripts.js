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

function editReply(post_id, originalContent, parent_id, type) {
    const commentContentElement = document.getElementById(`comment-content-${parent_id}`);
    commentContentElement.innerHTML = `
        <form class = "pure-form" method="POST" action="/updateReply/${post_id}/${parent_id}">
            <textarea type="text" id="edit-comment-${parent_id}" name="editArea"> ${originalContent} </textarea>
            <button class="pure-button pure-button-primary" onclick="cancelEdit(${parent_id}, '${originalContent}')">Cancel</button>
            <input class="pure-button pure-button-primary" type="submit" id="submit" name="submit" value="save">
            <input type="hidden" name="type" value="${type}">
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

function cancelReply(post_id){ 
    const replyBox = document.getElementById(`comment-reply-${post_id}`);
    replyBox.innerHTML = '';
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

function replyTo(review_id, parent_id,type){
    const replyBox = document.getElementById(`comment-reply-${parent_id}`);
    replyBox.innerHTML = `
        <form class = "pure-form" method="POST" action="/inlineReply/${review_id}/${parent_id}">
        <textarea type="text" id="inline_reply" name="reply"></textarea>
        <button class="pure-button pure-button-primary" onclick="cancelReply(${parent_id})">Cancel</button>
        <input class="pure-button pure-button-primary" type="submit" id="submit" name="submit" value="Reply">
        <input type="hidden" name="type" value="${type}">
        </form>
    `;
}
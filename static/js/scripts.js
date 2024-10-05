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
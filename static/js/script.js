let stars = document.getElementsByClassName("star");

// Funtion to update rating
function rate(n) {
    remove();
    var rating = document.getElementById("rating");
    for (let i = 0; i < n; i++) {
        console.log("here")
        if (n == 1) cls = "one";
        else if (n == 2) cls = "two";
        else if (n == 3) cls = "three";
        else if (n == 4) cls = "four";
        else if (n == 5) cls = "five";
        stars[i].className = "star " + cls;
    }
    rating.value = n;
}
 
// To remove the pre-applied styling
function remove() {
    let i = 0;
    while (i < 5) {
        stars[i].className = "star";
        i++;
    }
}
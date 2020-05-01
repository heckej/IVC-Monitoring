function toggleTopBarOnScroll() {
    // Set delay
    d = new Date();
    millisNow = d.getTime();
    differenceMillis = millisNow - millisStart;
    limit = 500;
    console.log(differenceMillis);
    topBar = document.getElementsByClassName("top-bar")[0];
    dropdown = document.getElementById("drop-down");
    newScrollTop = window.scrollY;
    if(scrollTop > newScrollTop) {
        if(differenceMillis > limit) {
            topBar.style.position = "fixed";
            topBar.style.top = "0px";
            topBar.style.width = "100%";
            console.log("up");
            millisStart = millisNow;
        }
    } else if(!dropdown.classList.contains("top-app-bar__icon-active")) {
       topBar.style.position = "absolute";
       topBar.style.width = "100%";
       topBar.style.top = newScrollTop;
       console.log("down");
    }
    if(newScrollTop == 0) {
        topBar.style.position = "";
        topBar.style.top = "";
        topBar.style.width = "";
    }
    scrollTop = newScrollTop;
}
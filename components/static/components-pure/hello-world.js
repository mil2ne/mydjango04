(function () {
  document.querySelectorAll(".hello-world-component h1").forEach(el => {
    el.onclick = function (e) {
      alert(e.target.textContent);
    };
  });
})()
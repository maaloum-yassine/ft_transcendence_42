
const team = () => {

var swiper = new Swiper(".swiper", {
	grabCursor: true,
	initialSlide: 4,
	centeredSlides: true,
	slidesPerView: "auto",
	spaceBetween: 10,
	speed: 1000,
	freeMode: false,
	mousewheel: {
	  thresholdDelta: 30,
	},
	pagination: {
	  el: ".swiper-pagination",
	},
	on: {
	  click(event) {
		swiper.slideTo(this.clickedIndex);
	  },
	},
  })
  const profilePhoto = document.getElementById("profilePhoto");
  fetch(`https://${window.location.host}/api/profile/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  })
    .then((response) => response.json())
    .then((data) => {
      if (profilePhoto && data.data.avatar) {
          profilePhoto.src = data.data.avatar;
          profilePhoto.style.display = "block";
      }
    })
    .catch(() => {
      console.log("Error Upload Avatar")
    });
};

export default team;

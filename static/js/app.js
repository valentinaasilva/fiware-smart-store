(function () {
	var THEME_KEY = "smartstore-theme";

	function applyTheme(theme) {
		if (theme === "dark") {
			document.body.classList.add("theme-dark");
		} else {
			document.body.classList.remove("theme-dark");
		}
	}

	function initThemeToggle() {
		var button = document.getElementById("theme-toggle");
		if (!button) {
			return;
		}

		function updateButtonLabel() {
			var isDark = document.body.classList.contains("theme-dark");
			button.textContent = isDark ? button.dataset.light : button.dataset.dark;
		}

		var savedTheme = localStorage.getItem(THEME_KEY);
		if (savedTheme === "dark" || savedTheme === "light") {
			applyTheme(savedTheme);
		}

		updateButtonLabel();

		button.addEventListener("click", function () {
			var isDark = document.body.classList.toggle("theme-dark");
			localStorage.setItem(THEME_KEY, isDark ? "dark" : "light");
			updateButtonLabel();
		});
	}

	function initStoreMap() {
		var mapNode = document.getElementById("store-map");
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		var lat = parseFloat(mapNode.dataset.lat || "");
		var lng = parseFloat(mapNode.dataset.lng || "");
		var title = mapNode.dataset.title || "Store";

		if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
			return;
		}

		if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
			return;
		}

		var map = window.L.map(mapNode).setView([lat, lng], 14);
		window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		}).addTo(map);

		window.L.marker([lat, lng]).addTo(map).bindPopup(title).openPopup();
	}

	function initDashboardStoresMap() {
		var mapNode = document.getElementById("dashboard-stores-map");
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		var rawMarkers = mapNode.dataset.markers || "[]";
		var markers;

		try {
			markers = JSON.parse(rawMarkers);
		} catch (error) {
			return;
		}

		if (!Array.isArray(markers) || markers.length === 0) {
			return;
		}

		var first = markers[0];
		var map = window.L.map(mapNode).setView([first.lat, first.lng], 5);
		window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		}).addTo(map);

		var bounds = [];
		markers.forEach(function (marker) {
			if (
				!marker ||
				typeof marker.lat !== "number" ||
				typeof marker.lng !== "number"
			) {
				return;
			}

			if (marker.lat < -90 || marker.lat > 90 || marker.lng < -180 || marker.lng > 180) {
				return;
			}

			bounds.push([marker.lat, marker.lng]);
			window.L.marker([marker.lat, marker.lng]).addTo(map).bindPopup(marker.name || "Store");
		});

		if (bounds.length > 1) {
			map.fitBounds(bounds, { padding: [20, 20] });
		}
	}

	document.addEventListener("DOMContentLoaded", function () {
		initThemeToggle();
		initStoreMap();
		initDashboardStoresMap();
	});
})();

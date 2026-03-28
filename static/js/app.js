(function () {
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

	document.addEventListener("DOMContentLoaded", initStoreMap);
})();

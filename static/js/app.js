(function () {
	var THEME_KEY = "smartstore-theme-mode";

	function getSystemTheme() {
		if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
			return "dark";
		}
		return "light";
	}

	function applyThemeMode(mode) {
		var effective = mode === "system" ? getSystemTheme() : mode;
		if (effective === "dark") {
			document.body.classList.add("theme-dark");
		} else {
			document.body.classList.remove("theme-dark");
		}
	}

	function initThemeToggle() {
		var selector = document.getElementById("theme-mode");
		if (!selector) {
			return;
		}

		var savedMode = localStorage.getItem(THEME_KEY);
		var mode = savedMode === "dark" || savedMode === "light" || savedMode === "system" ? savedMode : "system";
		selector.value = mode;
		applyThemeMode(mode);

		selector.addEventListener("change", function () {
			var nextMode = selector.value;
			localStorage.setItem(THEME_KEY, nextMode);
			applyThemeMode(nextMode);
		});

		if (window.matchMedia) {
			window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
				if ((localStorage.getItem(THEME_KEY) || "system") === "system") {
					applyThemeMode("system");
				}
			});
		}
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

	function initMermaidDiagrams() {
		if (typeof window.mermaid !== "undefined") {
			window.mermaid.initialize({ startOnLoad: true, theme: 'default' });
			window.mermaid.contentLoaded();
		}
	}

	document.addEventListener("DOMContentLoaded", function () {
		initThemeToggle();
		initStoreMap();
		initDashboardStoresMap();
		initMermaidDiagrams();
	});
})();

(function () {
	const THEME_KEY = "smartstore-theme-mode";

	function getSystemTheme() {
		if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
			return "dark";
		}
		return "light";
	}

	function applyThemeMode(mode) {
		const effective = mode === "system" ? getSystemTheme() : mode;
		if (effective === "dark") {
			document.body.classList.add("theme-dark");
		} else {
			document.body.classList.remove("theme-dark");
		}
	}

	function initThemeToggle() {
		const selector = document.getElementById("theme-mode");
		if (!selector) {
			return;
		}

		const savedMode = localStorage.getItem(THEME_KEY);
		let mode = savedMode === "dark" || savedMode === "light" || savedMode === "system" ? savedMode : "system";
		selector.value = mode;
		applyThemeMode(mode);

		selector.addEventListener("change", function () {
			const nextMode = selector.value;
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
		const mapNode = document.getElementById("store-map");
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		const lat = parseFloat(mapNode.dataset.lat || "");
		const lng = parseFloat(mapNode.dataset.lng || "");
		const title = mapNode.dataset.title || "Store";

		if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
			return;
		}

		if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
			return;
		}

		const map = window.L.map(mapNode).setView([lat, lng], 14);
		window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		}).addTo(map);

		window.L.marker([lat, lng]).addTo(map).bindPopup(title).openPopup();
	}

	function initDashboardStoresMap() {
		const mapNode = document.getElementById("dashboard-stores-map");
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		const rawMarkers = mapNode.dataset.markers || "[]";
		let markers;

		try {
			markers = JSON.parse(rawMarkers);
		} catch (error) {
			return;
		}

		if (!Array.isArray(markers) || markers.length === 0) {
			return;
		}

		const first = markers[0];
		const map = window.L.map(mapNode).setView([first.lat, first.lng], 5);
		window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		}).addTo(map);

		const bounds = [];
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
                    window.mermaid.initialize({
                            startOnLoad: true,
                            theme: 'base',
                            themeVariables: {
                                    primaryColor: '#0aa64f',
				    primaryTextColor: '#0f5c3f',
                                    primaryBorderColor: '#0f5c3f',
				    secondaryTextColor: '#0f5c3f',
				    tertiaryTextColor: '#0f5c3f',
                                    lineColor: '#2fc77b',
                                    secondBkgColor: '#e4f6e8',
                                    tertiaryColor: '#e4f6e8',
                                    background: '#ffffff',
                                    mainBkg: '#0aa64f',
                                    clusterBkg: '#e4f6e8',
                                    clusterBorder: '#0f5c3f',
                                    fontFamily: 'Manrope, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
                            },
                            securityLevel: 'loose'
                    });
                    window.mermaid.contentLoaded();
		}
	}

	function initConfirmForms() {
		const forms = document.querySelectorAll("form[data-confirm-message]");
		forms.forEach(function (form) {
			form.addEventListener("submit", function (event) {
				const message = form.getAttribute("data-confirm-message") || "";
				if (message && !window.confirm(message)) {
					event.preventDefault();
				}
			});
		});
	}

	document.addEventListener("DOMContentLoaded", function () {
		initThemeToggle();
		initStoreMap();
		initDashboardStoresMap();
		initMermaidDiagrams();
		initConfirmForms();
	});
})();

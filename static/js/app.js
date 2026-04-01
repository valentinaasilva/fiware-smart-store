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

	function escapeHtml(value) {
		return String(value || "").replace(/[&<>"']/g, function (character) {
			const entities = {
				"&": "&amp;",
				"<": "&lt;",
				">": "&gt;",
				'"': "&quot;",
				"'": "&#39;",
			};
			return entities[character] || character;
		});
	}

	function buildStoreAddressLine(marker) {
		if (!marker || !marker.address) {
			return "";
		}

		if (typeof marker.address === "string") {
			return marker.address;
		}

		const parts = [];
		if (marker.address.streetAddress) {
			parts.push(marker.address.streetAddress);
		}
		if (marker.address.addressLocality) {
			parts.push(marker.address.addressLocality);
		}
		if (marker.address.addressRegion) {
			parts.push(marker.address.addressRegion);
		}
		return parts.join(", ");
	}

	function getStoreMarkerIcon(marker, storeLabel) {
		const image = marker && marker.image ? escapeHtml(marker.image) : "";
		const name = marker && marker.name ? escapeHtml(marker.name) : escapeHtml(storeLabel || "Store");
		const fallback = escapeHtml(String(name).slice(0, 1).toUpperCase() || "S");
		const content = image
			? `<img src="${image}" alt="${name}">`
			: `<span class="store-map-marker-fallback">${fallback}</span>`;

		return window.L.divIcon({
			className: "store-map-marker-icon",
			html: `<div class="store-map-marker-frame">${content}</div>`,
			iconSize: [58, 58],
			iconAnchor: [29, 50],
			popupAnchor: [0, -44],
		});
	}

	function buildStoreHoverCardHtml(marker, openLabel, storeLabel) {
		const name = escapeHtml((marker && marker.name) || storeLabel || "Store");
		const image = marker && marker.image ? `<div class="store-marker-media"><img src="${escapeHtml(marker.image)}" alt="${name}"></div>` : "";
		const address = escapeHtml(buildStoreAddressLine(marker) || "-");
		const countryCode = escapeHtml((marker && marker.countryCode) || "-");
		const description = escapeHtml((marker && marker.description) || "");
		const hintLabel = escapeHtml(openLabel || "Open store detail");

		return `
			<div class="store-marker-card">
				${image}
				<div class="store-marker-body">
					<h4>${name}</h4>
					<div class="store-marker-meta">
						<span><i class="fa-solid fa-location-dot" aria-hidden="true"></i> ${address}</span>
						<span><i class="fa-solid fa-flag" aria-hidden="true"></i> ${countryCode}</span>
						${description ? `<span>${description}</span>` : ""}
					</div>
					<div class="store-marker-actions"><span>${hintLabel}</span></div>
				</div>
			</div>
		`;
	}

	function positionStoreHoverCard(cardNode, map, lat, lng) {
		if (!cardNode || !map) {
			return;
		}

		const mapSize = map.getSize();
		const point = map.latLngToContainerPoint([lat, lng]);
		const pad = 10;
		const gap = 14;

		cardNode.classList.add("is-visible");
		cardNode.style.left = "0px";
		cardNode.style.top = "0px";

		const cardWidth = cardNode.offsetWidth;
		const cardHeight = cardNode.offsetHeight;

		let left = point.x + gap;
		if (left + cardWidth > mapSize.x - pad) {
			left = point.x - cardWidth - gap;
		}
		if (left < pad) {
			left = pad;
		}

		let top = point.y - cardHeight - gap;
		if (top < pad) {
			top = point.y + gap;
		}
		if (top + cardHeight > mapSize.y - pad) {
			top = Math.max(pad, mapSize.y - cardHeight - pad);
		}

		cardNode.style.left = `${Math.round(left)}px`;
		cardNode.style.top = `${Math.round(top)}px`;
	}

	function initLeafletStoreMap(mapNode, options) {
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		let markers;
		try {
			markers = JSON.parse(mapNode.dataset.markers || "[]");
		} catch (_error) {
			return;
		}

		if (!Array.isArray(markers) || markers.length === 0) {
			return;
		}

		const firstMarker = markers[0];
		const map = window.L.map(mapNode).setView([firstMarker.lat, firstMarker.lng], options.defaultZoom || 5);
		window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		}).addTo(map);

		const hoverCard = document.createElement("div");
		hoverCard.className = "store-map-hover-card";
		mapNode.appendChild(hoverCard);
		let activeMarkerData = null;

		const bounds = [];
		markers.forEach(function (marker) {
			if (
				!marker ||
				typeof marker.lat !== "number" ||
				typeof marker.lng !== "number" ||
				marker.lat < -90 || marker.lat > 90 ||
				marker.lng < -180 || marker.lng > 180
			) {
				return;
			}

			bounds.push([marker.lat, marker.lng]);
			const leafletMarker = window.L.marker([marker.lat, marker.lng], {
				icon: getStoreMarkerIcon(marker, options.storeLabel),
				riseOnHover: true,
			}).addTo(map);

			leafletMarker.on("mouseover", function () {
				activeMarkerData = marker;
				hoverCard.innerHTML = buildStoreHoverCardHtml(marker, options.openLabel, options.storeLabel);
				positionStoreHoverCard(hoverCard, map, marker.lat, marker.lng);
			});
			leafletMarker.on("mouseout", function () {
				activeMarkerData = null;
				hoverCard.classList.remove("is-visible");
			});
			leafletMarker.on("click", function () {
				if (marker.detailUrl) {
					window.location.href = marker.detailUrl;
				}
			});
		});

		map.on("zoom move", function () {
			if (activeMarkerData) {
				positionStoreHoverCard(hoverCard, map, activeMarkerData.lat, activeMarkerData.lng);
			}
		});

		if (options.fitBounds !== false && bounds.length > 1) {
			map.fitBounds(bounds, { padding: [20, 20] });
		}

		return map;
	}

	function initStoreMap() {
		const mapNode = document.getElementById("store-map");
		if (!mapNode || typeof window.L === "undefined") {
			return;
		}

		const lat = parseFloat(mapNode.dataset.lat || "");
		const lng = parseFloat(mapNode.dataset.lng || "");
		const title = mapNode.dataset.title || mapNode.dataset.storeLabel || "Store";

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
		initLeafletStoreMap(mapNode, {
			defaultZoom: 5,
			fitBounds: true,
			openLabel: mapNode ? mapNode.dataset.openStoreLabel : "",
			storeLabel: mapNode ? mapNode.dataset.storeLabel : "",
		});
	}

	function initStoresMapPage() {
		const mapNode = document.getElementById("stores-map-page");
		initLeafletStoreMap(mapNode, {
			defaultZoom: 6,
			fitBounds: true,
			openLabel: mapNode ? mapNode.dataset.openStoreLabel : "",
			storeLabel: mapNode ? mapNode.dataset.storeLabel : "",
		});
	}

	function initStoreImmersiveScene() {
		const sceneNode = document.getElementById("store-immersive-scene");
		if (!sceneNode) {
			return;
		}
		const t = function (key, fallback) {
			const value = sceneNode.dataset[key];
			return value ? value : fallback;
		};
		const labels = {
			loadingScene: t("loadingScene", "Loading 3D scene..."),
			unableLayout: t("unableLayout", "Unable to load 3D layout."),
			webglDisabled: t("webglDisabled", "WebGL is disabled in this browser. Enable hardware acceleration to view 3D."),
			rendererError: t("rendererError", "Unable to initialize 3D renderer in this browser."),
			threejsError: t("threejsError", "Unable to load Three.js assets. Check network/CSP configuration."),
			unavailableBrowserNote: t("unavailableBrowserNote", "3D unavailable in this browser. Inventory overview remains available."),
			rendererFailedNote: t("rendererFailedNote", "3D renderer initialization failed. Inventory overview remains available."),
			assetsUnavailableNote: t("assetsUnavailableNote", "3D assets unavailable. Inventory overview remains available."),
			mainAisle: t("mainAisle", "Main aisle"),
			shelfPrefix: t("shelfPrefix", "Shelf"),
			productLabel: t("productLabel", "Product"),
			resume: t("resume", "Resume"),
			pause: t("pause", "Pause"),
			firstPersonOn: t("firstPersonOn", "First-Person: On"),
			firstPersonOff: t("firstPersonOff", "First-Person: Off"),
			tourRunning: t("tourRunning", "Tour running"),
			stopLabel: t("stop", "Stop"),
			tourPaused: t("tourPaused", "Tour paused"),
			tourIdle: t("tourIdle", "Tour idle"),
			tourStoppedFirstPerson: t("tourStoppedFirstPerson", "Tour stopped (first-person mode)"),
			firstPersonEnabled: t("firstPersonEnabled", "First-person mode enabled (WASD move, Q/E turn)"),
			orbitEnabled: t("orbitEnabled", "Orbit mode enabled"),
			tourStoppedManualCamera: t("tourStoppedManualCamera", "Tour stopped (manual camera control)"),
			tourStoppedManualZoom: t("tourStoppedManualZoom", "Tour stopped (manual zoom)"),
			firstPersonNavigationActive: t("firstPersonNavigationActive", "First-person navigation active"),
			orbitNavigationActive: t("orbitNavigationActive", "Orbit manual navigation active"),
			controlsHint: t("controlsHint", "Controls: drag to orbit, wheel to zoom, Start Tour for cinematic route, or enable first-person (WASD move, Q/E turn)."),
			shelfUnits: t("shelfUnits", "Shelf units"),
			totalStock: t("totalStock", "Total stock"),
			shelfKey: t("shelfKey", "Shelf"),
			stockKey: t("stockKey", "Stock"),
			inspectorHeading: t("inspectorHeading", "Shelf Product Overview"),
			emptyShelvesProducts: t("emptyShelvesProducts", "No shelves or products available."),
			loadFormat: t("loadFormat", "Load {current} / {max} ({percent}%)"),
			noProductsOnShelf: t("noProductsOnShelf", "No products on this shelf."),
		};
		const inspectorNode = document.getElementById("immersive-inspector");
		const tourStartButton = document.getElementById("immersive-tour-start");
		const tourPauseButton = document.getElementById("immersive-tour-pause");
		const tourResetButton = document.getElementById("immersive-tour-reset");
		const cameraModeButton = document.getElementById("immersive-camera-mode");
		const tourStatusNode = document.getElementById("immersive-tour-status");

		const loadLabel = sceneNode.querySelector(".scene-loading");
		if (loadLabel) {
			loadLabel.textContent = labels.loadingScene;
		}

		let layout = [];
		try {
			layout = JSON.parse(sceneNode.dataset.layout || "[]");
		} catch (_error) {
			sceneNode.innerHTML = `<p class="scene-loading">${escapeHtml(labels.unableLayout)}</p>`;
			renderImmersiveInspector(inspectorNode, [], null, labels);
			return;
		}

		renderImmersiveInspector(inspectorNode, layout, null, labels);

		loadThreeWithFallback(sceneNode)
			.then(function () {
				if (!isWebGLAvailable()) {
					sceneNode.innerHTML = `<p class="scene-loading">${escapeHtml(labels.webglDisabled)}</p>`;
					renderImmersiveInspector(inspectorNode, layout, {
						note: labels.unavailableBrowserNote,
					}, labels);
					return;
				}

				const width = sceneNode.clientWidth || 800;
				const height = 300;
				let renderer;
				try {
					renderer = new window.THREE.WebGLRenderer({ antialias: true, alpha: true });
				} catch (_error) {
					sceneNode.innerHTML = `<p class="scene-loading">${escapeHtml(labels.rendererError)}</p>`;
					renderImmersiveInspector(inspectorNode, layout, {
						note: labels.rendererFailedNote,
					}, labels);
					return;
				}

				renderer.setSize(width, height);
				renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
				sceneNode.innerHTML = "";
				sceneNode.appendChild(renderer.domElement);

				const scene = new window.THREE.Scene();
				scene.background = new window.THREE.Color("#edf2e8");

				const camera = new window.THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
				let cameraMode = "orbit";
				const cameraTarget = new window.THREE.Vector3(0, 1.5, 0);
				const cameraControl = {
					radius: 18,
					theta: 0,
					phi: 0.95,
				};
				const firstPerson = {
					x: 0,
					y: 1.62,
					z: 12,
					yaw: Math.PI,
				};
				const initialCamera = {
					targetX: 0,
					targetZ: 0,
					radius: 18,
					theta: 0,
					phi: 0.95,
					fpX: 0,
					fpY: 1.62,
					fpZ: 12,
					fpYaw: Math.PI,
				};

				function syncCamera() {
					if (cameraMode === "first-person") {
						firstPerson.x = Math.max(-6, Math.min(6, firstPerson.x));
						firstPerson.z = Math.max(-14, Math.min(14, firstPerson.z));
						camera.position.set(firstPerson.x, firstPerson.y, firstPerson.z);
						camera.lookAt(
							firstPerson.x + Math.sin(firstPerson.yaw),
							firstPerson.y,
							firstPerson.z + Math.cos(firstPerson.yaw)
						);
						return;
					}

					const radius = Math.max(8, Math.min(35, cameraControl.radius));
					const phi = Math.max(0.35, Math.min(1.35, cameraControl.phi));
					camera.position.set(
						cameraTarget.x + radius * Math.sin(phi) * Math.sin(cameraControl.theta),
						cameraTarget.y + radius * Math.cos(phi),
						cameraTarget.z + radius * Math.sin(phi) * Math.cos(cameraControl.theta)
					);
					camera.lookAt(cameraTarget);
				}
				syncCamera();

				const ambient = new window.THREE.AmbientLight(0xffffff, 0.62);
				scene.add(ambient);
				const directional = new window.THREE.DirectionalLight(0xffffff, 0.55);
				directional.position.set(0, 16, 0);
				scene.add(directional);

				const floor = new window.THREE.Mesh(
					new window.THREE.PlaneGeometry(48, 34),
					new window.THREE.MeshStandardMaterial({ color: 0xdfe6d7, roughness: 0.93 })
				);
				floor.rotation.x = -Math.PI / 2;
				scene.add(floor);

				const aisle = new window.THREE.Mesh(
					new window.THREE.PlaneGeometry(7.5, 30),
					new window.THREE.MeshStandardMaterial({ color: 0xcdd8c5, roughness: 0.88 })
				);
				aisle.rotation.x = -Math.PI / 2;
				aisle.position.y = 0.01;
				scene.add(aisle);

				const wallMaterial = new window.THREE.MeshStandardMaterial({ color: 0xf7faf5, roughness: 0.95 });
				const wallBack = new window.THREE.Mesh(new window.THREE.BoxGeometry(48, 6, 0.4), wallMaterial);
				wallBack.position.set(0, 3, -16.5);
				scene.add(wallBack);
				const wallFront = new window.THREE.Mesh(new window.THREE.BoxGeometry(48, 6, 0.4), wallMaterial);
				wallFront.position.set(0, 3, 16.5);
				scene.add(wallFront);
				const wallLeft = new window.THREE.Mesh(new window.THREE.BoxGeometry(0.4, 6, 33), wallMaterial);
				wallLeft.position.set(-23.8, 3, 0);
				scene.add(wallLeft);
				const wallRight = new window.THREE.Mesh(new window.THREE.BoxGeometry(0.4, 6, 33), wallMaterial);
				wallRight.position.set(23.8, 3, 0);
				scene.add(wallRight);

				const ceiling = new window.THREE.Mesh(
					new window.THREE.PlaneGeometry(48, 34),
					new window.THREE.MeshStandardMaterial({ color: 0xf9fcf8, roughness: 0.9 })
				);
				ceiling.rotation.x = Math.PI / 2;
				ceiling.position.y = 5.9;
				scene.add(ceiling);

				for (let lightIndex = -2; lightIndex <= 2; lightIndex += 1) {
					const laneLight = new window.THREE.PointLight(0xffffff, 0.35, 18, 2);
					laneLight.position.set(0, 5.4, lightIndex * 6);
					scene.add(laneLight);

					const lightCover = new window.THREE.Mesh(
						new window.THREE.CylinderGeometry(0.32, 0.32, 0.18, 16),
						new window.THREE.MeshStandardMaterial({ color: 0xf2f5ef, roughness: 0.45 })
					);
					lightCover.position.set(0, 5.6, lightIndex * 6);
					scene.add(lightCover);
				}

				const shelfGroup = new window.THREE.Group();
				const productMeshes = [];
				const shelfPairCount = Math.max(Math.ceil(layout.length / 2), 1);
				const rowSpacing = Math.min(5.4, Math.max(3.6, 22 / shelfPairCount));
				const sideOffset = 4.8;
				const waypoints = [];
				let selectedMesh = null;

				(layout || []).forEach(function (shelf, shelfIndex) {
					const rowIndex = Math.floor(shelfIndex / 2);
					const side = shelfIndex % 2 === 0 ? -1 : 1;
					const x = side * sideOffset;
					const z = rowIndex * rowSpacing - ((shelfPairCount - 1) * rowSpacing) / 2;
					const shelfFill = Math.max(0, Math.min(100, Number(shelf.fillPercent || 0)));
					waypoints.push({
						targetX: side * -1.8,
						targetZ: z,
						theta: side === -1 ? -0.72 : 0.72,
						radius: 11.5,
						phi: 0.92,
						shelfName: shelf.name || `Shelf ${shelfIndex + 1}`,
					});

					const shelfBaseColor = shelfFill > 85 ? 0xcf6a47 : 0x74975c;
					const shelfBody = new window.THREE.Mesh(
						new window.THREE.BoxGeometry(2.7, 2.9, 1.2),
						new window.THREE.MeshStandardMaterial({ color: shelfBaseColor, roughness: 0.64 })
					);
					shelfBody.position.set(x, 1.45, z);
					shelfGroup.add(shelfBody);

					[0.4, 1.1, 1.8, 2.5].forEach(function (yLevel) {
						const board = new window.THREE.Mesh(
							new window.THREE.BoxGeometry(2.9, 0.1, 1.25),
							new window.THREE.MeshStandardMaterial({ color: 0xbec9b3, roughness: 0.7 })
						);
						board.position.set(x, yLevel, z);
						shelfGroup.add(board);
					});

					const shelfSign = new window.THREE.Mesh(
						new window.THREE.BoxGeometry(1.6, 0.34, 0.08),
						new window.THREE.MeshStandardMaterial({ color: 0x243225, roughness: 0.45 })
					);
					shelfSign.position.set(x, 3.2, z + side * -0.5);
					shelfGroup.add(shelfSign);

					const products = Array.isArray(shelf.products) ? shelf.products : [];
					products.slice(0, 12).forEach(function (product, productIndex) {
						const count = Number(product.shelfCount || 0);
						const stockCount = Number(product.stockCount || 0);
						const level = productIndex % 4;
						const column = Math.floor(productIndex / 4);
						const yLevel = 0.65 + level * 0.68;
						const zOffset = -0.42 + column * 0.28;
						const heightScale = Math.max(0.22, Math.min(0.95, 0.2 + count * 0.05));
						const widthScale = Math.max(0.2, Math.min(0.36, 0.22 + (stockCount % 4) * 0.03));
						const stockRisk = stockCount <= 3 ? 0xe14747 : stockCount <= 8 ? 0xf1a64a : 0x0aa64f;
						const productMesh = new window.THREE.Mesh(
							new window.THREE.BoxGeometry(widthScale, heightScale, 0.23),
							new window.THREE.MeshStandardMaterial({
								color: stockRisk,
								roughness: 0.3,
								emissive: 0x000000,
							})
						);
						productMesh.position.set(x + side * -0.5, yLevel + heightScale / 2, z + zOffset);
						const productKey = `${String(shelf.id || shelf.name || shelfIndex)}::${String(product.name || productIndex)}`;
						productMesh.userData = {
							name: product.name || "Product",
							shelfCount: count,
							stockCount: stockCount,
							shelfName: shelf.name || "Shelf",
							productKey: productKey,
						};
						productMeshes.push(productMesh);
						shelfGroup.add(productMesh);
					});
				});
				scene.add(shelfGroup);

				if (waypoints.length === 0) {
					waypoints.push({
						targetX: 0,
						targetZ: 0,
						theta: 0,
						radius: 14,
						phi: 0.95,
						shelfName: labels.mainAisle,
					});
				}

				const tourState = {
					active: false,
					paused: false,
					index: 0,
					holdMs: 0,
					segmentMs: 0,
					segmentDurationMs: 1800,
					segmentActive: false,
					segmentFrom: null,
					segmentTo: null,
					lastFrameMs: 0,
				};

				function easeInOutCubic(t) {
					if (t < 0.5) {
						return 4 * t * t * t;
					}
					const p = -2 * t + 2;
					return 1 - (p * p * p) / 2;
				}

				function lerp(start, end, t) {
					return start + (end - start) * t;
				}

				function captureOrbitPose() {
					return {
						targetX: cameraTarget.x,
						targetZ: cameraTarget.z,
						theta: cameraControl.theta,
						radius: cameraControl.radius,
						phi: cameraControl.phi,
					};
				}

				function beginTourSegment(nextWaypoint) {
					tourState.segmentFrom = captureOrbitPose();
					tourState.segmentTo = {
						targetX: nextWaypoint.targetX,
						targetZ: nextWaypoint.targetZ,
						theta: nextWaypoint.theta,
						radius: nextWaypoint.radius,
						phi: nextWaypoint.phi,
					};
					tourState.segmentMs = 0;
					tourState.segmentActive = true;
				}

				function setTourStatus(message) {
					if (tourStatusNode) {
						tourStatusNode.textContent = message;
					}
				}

				function setPauseLabel() {
					if (!tourPauseButton) {
						return;
					}
					tourPauseButton.textContent = tourState.paused ? labels.resume : labels.pause;
				}

				function updateCameraModeButton() {
					if (!cameraModeButton) {
						return;
					}
					const isFirstPerson = cameraMode === "first-person";
					cameraModeButton.textContent = isFirstPerson ? labels.firstPersonOn : labels.firstPersonOff;
					cameraModeButton.classList.toggle("is-active", isFirstPerson);
				}

				function stopTour(reason) {
					tourState.active = false;
					tourState.paused = false;
					tourState.holdMs = 0;
					tourState.segmentMs = 0;
					tourState.segmentActive = false;
					tourState.segmentFrom = null;
					tourState.segmentTo = null;
					setPauseLabel();
					if (reason) {
						setTourStatus(reason);
					}
				}

				function startTour() {
					cameraMode = "orbit";
					updateCameraModeButton();
					tourState.active = true;
					tourState.paused = false;
					tourState.holdMs = 0;
					tourState.segmentMs = 0;
					tourState.segmentActive = false;
					tourState.lastFrameMs = 0;
					setPauseLabel();
					const current = waypoints[tourState.index] || waypoints[0];
					beginTourSegment(current);
					setTourStatus(`${labels.tourRunning} - ${labels.stopLabel.toLowerCase()} ${tourState.index + 1}/${waypoints.length}: ${current.shelfName}`);
				}

				function pauseOrResumeTour() {
					if (!tourState.active) {
						startTour();
						return;
					}
					tourState.paused = !tourState.paused;
					setPauseLabel();
					if (tourState.paused) {
						setTourStatus(labels.tourPaused);
						return;
					}
					const current = waypoints[tourState.index] || waypoints[0];
					setTourStatus(`${labels.tourRunning} - ${labels.stopLabel.toLowerCase()} ${tourState.index + 1}/${waypoints.length}: ${current.shelfName}`);
				}

				function resetTour() {
					tourState.active = false;
					tourState.paused = false;
					tourState.index = 0;
					tourState.holdMs = 0;
					tourState.segmentMs = 0;
					tourState.segmentActive = false;
					tourState.segmentFrom = null;
					tourState.segmentTo = null;
					tourState.lastFrameMs = 0;
					cameraTarget.x = initialCamera.targetX;
					cameraTarget.z = initialCamera.targetZ;
					cameraControl.radius = initialCamera.radius;
					cameraControl.theta = initialCamera.theta;
					cameraControl.phi = initialCamera.phi;
					firstPerson.x = initialCamera.fpX;
					firstPerson.y = initialCamera.fpY;
					firstPerson.z = initialCamera.fpZ;
					firstPerson.yaw = initialCamera.fpYaw;
					syncCamera();
					setPauseLabel();
					setTourStatus(labels.tourIdle);
				}

				if (tourStartButton) {
					tourStartButton.addEventListener("click", startTour);
				}
				if (tourPauseButton) {
					tourPauseButton.addEventListener("click", pauseOrResumeTour);
					setPauseLabel();
				}
				if (tourResetButton) {
					tourResetButton.addEventListener("click", resetTour);
				}
				if (cameraModeButton) {
					cameraModeButton.addEventListener("click", function () {
						cameraMode = cameraMode === "first-person" ? "orbit" : "first-person";
						updateCameraModeButton();
						if (cameraMode === "first-person") {
							stopTour(labels.tourStoppedFirstPerson);
							setTourStatus(labels.firstPersonEnabled);
						} else {
							setTourStatus(labels.orbitEnabled);
						}
						syncCamera();
					});
				}
				updateCameraModeButton();
				setTourStatus(labels.tourIdle);

				const label = document.createElement("p");
				label.className = "scene-hint";
				label.textContent = labels.controlsHint;
				sceneNode.appendChild(label);

				const raycaster = new window.THREE.Raycaster();
				const pointer = new window.THREE.Vector2();
				let isDragging = false;
				let hasMoved = false;
				const dragState = { x: 0, y: 0 };
				const keyState = {
					ArrowUp: false,
					ArrowDown: false,
					ArrowLeft: false,
					ArrowRight: false,
					w: false,
					a: false,
					s: false,
					d: false,
					q: false,
					e: false,
				};

				renderer.domElement.setAttribute("tabindex", "0");
				renderer.domElement.style.outline = "none";
				function pointerFromEvent(event) {
					const rect = renderer.domElement.getBoundingClientRect();
					pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
					pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
					raycaster.setFromCamera(pointer, camera);
					const intersections = raycaster.intersectObjects(productMeshes);
					return intersections.find(function (candidate) {
						return candidate.object && candidate.object.userData && candidate.object.userData.name;
					});
				}

				function updateActiveProduct(nextMesh) {
					if (selectedMesh && selectedMesh.material && selectedMesh.material.emissive) {
						selectedMesh.material.emissive.setHex(0x000000);
					}
					selectedMesh = nextMesh || null;
					if (selectedMesh && selectedMesh.material && selectedMesh.material.emissive) {
						selectedMesh.material.emissive.setHex(0x0f5c3f);
					}

					if (!selectedMesh) {
						setInspectorActiveProduct(inspectorNode, "");
						return;
					}
					const activeMeta = selectedMesh.userData || {};
					setInspectorActiveProduct(inspectorNode, activeMeta.productKey || "");
				}

				renderer.domElement.addEventListener("mousemove", function (event) {
					if (isDragging) {
						stopTour(labels.tourStoppedManualCamera);
						const dx = event.clientX - dragState.x;
						const dy = event.clientY - dragState.y;
						hasMoved = hasMoved || Math.abs(dx) > 1 || Math.abs(dy) > 1;
						if (cameraMode === "first-person") {
							firstPerson.yaw -= dx * 0.005;
						} else {
							cameraControl.theta -= dx * 0.006;
							cameraControl.phi -= dy * 0.004;
						}
						dragState.x = event.clientX;
						dragState.y = event.clientY;
						syncCamera();
						return;
					}

					const hit = pointerFromEvent(event);
					if (hit && hit.object && hit.object.userData) {
						const meta = hit.object.userData;
						label.textContent = `${meta.shelfName} | ${meta.name} - ${labels.shelfKey.toLowerCase()}: ${meta.shelfCount} | ${labels.stockKey.toLowerCase()}: ${meta.stockCount}`;
						return;
					}
					label.textContent = labels.controlsHint;
				});

				renderer.domElement.addEventListener("mousedown", function (event) {
					isDragging = true;
					hasMoved = false;
					dragState.x = event.clientX;
					dragState.y = event.clientY;
					renderer.domElement.focus();
				});

				window.addEventListener("mouseup", function () {
					isDragging = false;
				});

				renderer.domElement.addEventListener("wheel", function (event) {
					event.preventDefault();
					stopTour(labels.tourStoppedManualZoom);
					if (cameraMode === "first-person") {
						return;
					}
					cameraControl.radius += event.deltaY * 0.015;
					syncCamera();
				}, { passive: false });

				renderer.domElement.addEventListener("keydown", function (event) {
					const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
					if (Object.prototype.hasOwnProperty.call(keyState, key)) {
						keyState[key] = true;
					}
				});

				renderer.domElement.addEventListener("keyup", function (event) {
					const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
					if (Object.prototype.hasOwnProperty.call(keyState, key)) {
						keyState[key] = false;
					}
				});

				renderer.domElement.addEventListener("blur", function () {
					Object.keys(keyState).forEach(function (key) {
						keyState[key] = false;
					});
				});

				renderer.domElement.addEventListener("click", function (event) {
					if (hasMoved) {
						return;
					}
					const hit = pointerFromEvent(event);
					if (hit && hit.object) {
						updateActiveProduct(hit.object);
						const meta = hit.object.userData || {};
						label.textContent = `${meta.shelfName} | ${meta.name} - ${labels.shelfKey.toLowerCase()}: ${meta.shelfCount} | ${labels.stockKey.toLowerCase()}: ${meta.stockCount}`;
						return;
					}
					updateActiveProduct(null);
				});

				function updateKeyboardMovement() {
					if (tourState.active) {
						return;
					}
					const moveStep = cameraMode === "first-person" ? 0.11 : 0.14;
					let moved = false;
					if (cameraMode === "first-person") {
						const forwardX = Math.sin(firstPerson.yaw);
						const forwardZ = Math.cos(firstPerson.yaw);
						const strafeX = Math.sin(firstPerson.yaw + Math.PI / 2);
						const strafeZ = Math.cos(firstPerson.yaw + Math.PI / 2);
						if (keyState.w || keyState.ArrowUp) {
							firstPerson.x += forwardX * moveStep;
							firstPerson.z += forwardZ * moveStep;
							moved = true;
						}
						if (keyState.s || keyState.ArrowDown) {
							firstPerson.x -= forwardX * moveStep;
							firstPerson.z -= forwardZ * moveStep;
							moved = true;
						}
						if (keyState.a) {
							firstPerson.x -= strafeX * moveStep;
							firstPerson.z -= strafeZ * moveStep;
							moved = true;
						}
						if (keyState.d) {
							firstPerson.x += strafeX * moveStep;
							firstPerson.z += strafeZ * moveStep;
							moved = true;
						}
						if (keyState.q || keyState.ArrowLeft) {
							firstPerson.yaw += 0.034;
							moved = true;
						}
						if (keyState.e || keyState.ArrowRight) {
							firstPerson.yaw -= 0.034;
							moved = true;
						}
					} else {
						if (keyState.w || keyState.ArrowUp) {
							cameraTarget.z -= moveStep;
							moved = true;
						}
						if (keyState.s || keyState.ArrowDown) {
							cameraTarget.z += moveStep;
							moved = true;
						}
						if (keyState.a || keyState.ArrowLeft) {
							cameraTarget.x -= moveStep;
							moved = true;
						}
						if (keyState.d || keyState.ArrowRight) {
							cameraTarget.x += moveStep;
							moved = true;
						}
						cameraTarget.x = Math.max(-6, Math.min(6, cameraTarget.x));
						cameraTarget.z = Math.max(-14, Math.min(14, cameraTarget.z));
					}
					if (moved) {
						syncCamera();
						setTourStatus(cameraMode === "first-person" ? labels.firstPersonNavigationActive : labels.orbitNavigationActive);
					}
				}

				function updateGuidedTour(now) {
					if (!tourState.active || tourState.paused) {
						tourState.lastFrameMs = now;
						return;
					}
					if (cameraMode !== "orbit") {
						tourState.lastFrameMs = now;
						return;
					}

					const frameDelta = tourState.lastFrameMs ? Math.min(100, now - tourState.lastFrameMs) : 16;
					tourState.lastFrameMs = now;

					const targetWaypoint = waypoints[tourState.index] || waypoints[0];
					if (!tourState.segmentActive) {
						beginTourSegment(targetWaypoint);
					}

					tourState.segmentMs += frameDelta;
					const progress = Math.min(1, tourState.segmentMs / tourState.segmentDurationMs);
					const eased = easeInOutCubic(progress);
					const from = tourState.segmentFrom || captureOrbitPose();
					const to = tourState.segmentTo || targetWaypoint;
					cameraTarget.x = lerp(from.targetX, to.targetX, eased);
					cameraTarget.z = lerp(from.targetZ, to.targetZ, eased);
					cameraControl.theta = lerp(from.theta, to.theta, eased);
					cameraControl.radius = lerp(from.radius, to.radius, eased);
					cameraControl.phi = lerp(from.phi, to.phi, eased);
					syncCamera();

					setTourStatus(`${labels.tourRunning} - ${labels.stopLabel.toLowerCase()} ${tourState.index + 1}/${waypoints.length}: ${targetWaypoint.shelfName}`);

					if (progress >= 1) {
						tourState.segmentActive = false;
						tourState.holdMs += frameDelta;
						if (tourState.holdMs >= 1200) {
							tourState.holdMs = 0;
							tourState.index = (tourState.index + 1) % waypoints.length;
						}
						return;
					}
					tourState.holdMs = 0;
				}

				function animate(now) {
					updateGuidedTour(Number(now) || 0);
					updateKeyboardMovement();
					renderer.render(scene, camera);
					window.requestAnimationFrame(animate);
				}
				animate();

				window.addEventListener("resize", function () {
					const nextWidth = sceneNode.clientWidth || width;
					renderer.setSize(nextWidth, height);
					camera.aspect = nextWidth / height;
					camera.updateProjectionMatrix();
				});
			})
			.catch(function () {
				sceneNode.innerHTML = `<p class="scene-loading">${escapeHtml(labels.threejsError)}</p>`;
				renderImmersiveInspector(inspectorNode, layout, {
					note: labels.assetsUnavailableNote,
				}, labels);
			});
	}

	function renderImmersiveInspector(inspectorNode, layout, options, labels) {
		if (!inspectorNode) {
			return;
		}
		const i18n = labels || {};
		const headingLabel = i18n.inspectorHeading || "Shelf Product Overview";
		const emptyLabel = i18n.emptyShelvesProducts || "No shelves or products available.";
		const shelfPrefix = i18n.shelfPrefix || "Shelf";
		const loadFormat = i18n.loadFormat || "Load {current} / {max} ({percent}%)";
		const noProductsOnShelf = i18n.noProductsOnShelf || "No products on this shelf.";
		const productLabel = i18n.productLabel || "Product";
		const shelfUnitsLabel = i18n.shelfUnits || "Shelf units";
		const totalStockLabel = i18n.totalStock || "Total stock";

		const note = options && options.note ? options.note : "";
		inspectorNode.innerHTML = "";

		const heading = document.createElement("h4");
		heading.textContent = headingLabel;
		inspectorNode.appendChild(heading);

		if (note) {
			const noteNode = document.createElement("p");
			noteNode.className = "scene-loading";
			noteNode.textContent = note;
			inspectorNode.appendChild(noteNode);
		}

		if (!Array.isArray(layout) || layout.length === 0) {
			const emptyNode = document.createElement("p");
			emptyNode.className = "scene-loading";
			emptyNode.textContent = emptyLabel;
			inspectorNode.appendChild(emptyNode);
			return;
		}

		layout.forEach(function (shelf, shelfIndex) {
			const shelfCard = document.createElement("article");
			shelfCard.className = "immersive-shelf-card";

			const title = document.createElement("h5");
			title.className = "immersive-shelf-title";
			title.textContent = shelf.name || `${shelfPrefix} ${shelfIndex + 1}`;
			shelfCard.appendChild(title);

			const meta = document.createElement("p");
			meta.className = "immersive-shelf-meta";
			meta.textContent = loadFormat
				.replace("{current}", String(Number(shelf.currentLoad || 0)))
				.replace("{max}", String(Number(shelf.maxCapacity || 0)))
				.replace("{percent}", String(Number(shelf.fillPercent || 0)));
			shelfCard.appendChild(meta);

			const products = Array.isArray(shelf.products) ? shelf.products : [];
			if (products.length === 0) {
				const none = document.createElement("p");
				none.className = "immersive-shelf-meta";
				none.textContent = noProductsOnShelf;
				shelfCard.appendChild(none);
				inspectorNode.appendChild(shelfCard);
				return;
			}

			const list = document.createElement("ul");
			list.className = "immersive-products";
			products.forEach(function (product, productIndex) {
				const item = document.createElement("li");
				item.className = "immersive-product-row";
				const key = `${String(shelf.id || shelf.name || shelfIndex)}::${String(product.name || productIndex)}`;
				item.dataset.productKey = key;

				const nameNode = document.createElement("strong");
				nameNode.textContent = product.name || productLabel;
				item.appendChild(nameNode);

				const countsNode = document.createElement("span");
				countsNode.textContent = `${shelfUnitsLabel}: ${Number(product.shelfCount || 0)} | ${totalStockLabel}: ${Number(product.stockCount || 0)}`;
				item.appendChild(countsNode);
				list.appendChild(item);
			});

			shelfCard.appendChild(list);
			inspectorNode.appendChild(shelfCard);
		});
	}

	function setInspectorActiveProduct(inspectorNode, productKey) {
		if (!inspectorNode) {
			return;
		}
		const rows = inspectorNode.querySelectorAll(".immersive-product-row");
		rows.forEach(function (row) {
			if (productKey && row.dataset.productKey === productKey) {
				row.classList.add("is-active");
				return;
			}
			row.classList.remove("is-active");
		});
	}

	function isWebGLAvailable() {
		const canvas = document.createElement("canvas");
		try {
			return Boolean(
				window.WebGLRenderingContext &&
				(canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
			);
		} catch (_error) {
			return false;
		}
	}

	function loadThreeWithFallback(sceneNode) {
		if (typeof window.THREE !== "undefined") {
			return Promise.resolve();
		}

		const existingLoader = sceneNode.dataset.threeLoading;
		if (existingLoader === "1") {
			return Promise.reject(new Error("three-loading-in-progress"));
		}
		sceneNode.dataset.threeLoading = "1";

		const candidates = [
			"/static/vendor/three.min.js",
			"https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
			"https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js",
		];

		let index = 0;
		return new Promise(function (resolve, reject) {
			function tryNext() {
				if (typeof window.THREE !== "undefined") {
					sceneNode.dataset.threeLoading = "0";
					resolve();
					return;
				}
				if (index >= candidates.length) {
					sceneNode.dataset.threeLoading = "0";
					reject(new Error("three-cdn-unreachable"));
					return;
				}

				const url = candidates[index++];
				const script = document.createElement("script");
				script.src = url;
				script.async = true;
				script.onload = function () {
					if (typeof window.THREE !== "undefined") {
						sceneNode.dataset.threeLoading = "0";
						resolve();
						return;
					}
					tryNext();
				};
				script.onerror = tryNext;
				document.head.appendChild(script);
			}

			tryNext();
		});
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
		initStoresMapPage();
		initStoreImmersiveScene();
		initMermaidDiagrams();
		initConfirmForms();
	});
})();

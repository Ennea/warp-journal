document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        VERSION: '1.0.1',

        // raw data from the backend
        bannerTypes: {},
        statistics: {},
        pity: [],
        lowPity: [],
        warpHistory: [],
        totalWarps: 0,

        // frontend and processed data
        dataLoaded: false,
        showUpdateNotification: false,
        backendStatus: 0,
        backendMessage: '',
        requestInProgress: false,
        warpHistoryURL: '',
        manualUpdate: false,

        uidData: {},
        selectedUID: null,
        bannerTypesList: [],
        warpHistoryPageSize: 50,
        warpHistoryLastPage: 0,
        warpHistoryPage: 0,
        pagedWarpHistory: [],

        uidSelectorOpen: false,
        availableUIDs: [],
        columnSettingsOpen: {
            rarity: false,
            type: false,
            bannerType: false
        },
        // filters consist of a key:value pair for every value a given
        // column can be filtered for. a value of true means that the
        // filter for that column value is enabled, aka being displayed
        // inside the table. the special __formatter key is for transforming
        // the name of the key into a proper value that the real data can
        // be compared against
        columnFilters: {
            rarity: {
                __formatter: (key) => parseInt(key.substring(1)),
                _3: true,
                _4: true,
                _5: true
            },
            type: {
                __formatter: (key) => key.replace('_', ' '),
                Character: true,
                Light_Cone: true
            },
            bannerType: {
                __formatter: (key) => parseInt(key.substring(1))
            }
        },

        // methods
        init() {
            this.$refs.dataContainer.classList.remove('hidden');
            this.loadData();

            // check if a newer version is available
            fetch('https://api.github.com/repos/Ennea/warp-journal/releases/latest').then((response) => {
                if (response.status == 200) {
                    return response.json();
                }
            }).then((json) => {
                if (json && this.versionToNumber(json.tag_name) > this.versionToNumber(this.VERSION)) {
                    this.showUpdateNotification = true;
                }
            });

            // register a click handler on the document;
            // this handles closing column settings and the uid
            // selector when the user clicks on anything else on
            // the page besides the currently open column settings
            // or uid selector
            document.addEventListener('click', (event) => {
                if (this.uidSelectorOpen && !this.$refs.uidSelectorOptions.contains(event.target)) {
                    this.uidSelectorOpen = false;
                }

                for (const [ column, isOpen ] of Object.entries(this.columnSettingsOpen)) {
                    if (isOpen && !this.$refs['columnSettings_' + column].contains(event.target)) {
                        this.columnSettingsOpen[column] = false;
                    }
                }
            });

            // set up watches for any data relevant to the filter for the warp history
            for (const [ column, keys ] of Object.entries(this.columnFilters)) {
                if (column == 'bannerType') {
                    continue;
                }
                for (const key of Object.keys(keys)) {
                    if (key == '__formatter') {
                        continue;
                    }
                    this.$watch(`columnFilters.${column}['${key}']`, () => this.pageWarpHistory());
                }
            }

            // connect the websocket.
            // this websocket does not do anything by itself, but when
            // it is closed, the backend will automatically terminate
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
        },

        versionToNumber(version) {
            if (!version) {
                return null;
            }

            match = version.match(/^v?(\d{1,2})\.(\d{1,2})(?:\.(\d{1,2}))?$/);
            if (match == null) {
                return null;
            }

            version = parseInt(match[1]) * 1_0000 + parseInt(match[2]) * 1_00;
            if (match[3] != null) {
                version += parseInt(match[3]);
            }

            return version;
        },

        loadData() {
            fetch('/data', {
                cache: 'no-store'
            }).then((response) => {
                if (!response.ok) {
                    throw new Error();
                }
                return response.json();
            }).then((json) => {
                this.bannerTypes = json.bannerTypes;
                // create filters for the banner types and set up watches
                this.bannerTypesList = [];
                for (const [ key, name ] of Object.entries(this.bannerTypes)) {
                    this.bannerTypesList.push({ key, name });
                    if (!(key in this.columnFilters.bannerType)) {
                        this.$watch(`columnFilters.bannerType._${key}`, () => this.pageWarpHistory());
                    }
                    this.columnFilters.bannerType[`_${key}`] = true;
                }

                this.uidData = json.uids;
                this.availableUIDs = Object.keys(this.uidData);
                // calculate percentages & limit decimal places of average pity for the statistics
                for (const [ _, data ] of Object.entries(this.uidData)) {
                    for (const [ _, category ] of Object.entries(data.statistics)) {
                        if (data.totalWarps > 0) {
                            category.percent = (category.total / data.totalWarps * 100);
                            if (parseInt(category.percent) != category.percent) {
                                category.percent = category.percent.toFixed(2);
                            }
                        } else {
                            category.percent = 0;
                        }

                        if ('averagePity' in category && parseInt(category.averagePity) != category.averagePity) {
                            category.averagePity = category.averagePity.toFixed(1);
                        }
                    }
                }

                if (Object.keys(this.uidData).length > 0) {
                    this.selectUID(Object.keys(this.uidData)[0]);
                }
                this.dataLoaded = true;
            });
        },

        async updateWarps(event) {
            if (event) {
                event.preventDefault();
            }

            const body = {};
            if (this.manualUpdate) {
                body.url = this.warpHistoryURL;
            }

            const response = await this.doJsonRequest(fetch('/update-warp-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            }));
            if (!response) {
                return;
            }

            const json = await response.json();
            this.backendStatus = response.status;
            this.backendMessage = json?.message ?? 'An unknown error has occurred.';
            this.loadData();
        },

        async copyWarpsUrl(event) {
            if (event) {
                event.preventDefault();
            }

            const response = await this.doJsonRequest(fetch('/find-warp-history-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            }));
            if (!response) {
                return;
            }

            const json = await response.json();
            this.backendStatus = response.status;
            this.backendMessage = json?.message ?? '';
            if (json.url) {
                navigator.clipboard.writeText(json.url);
                this.backendMessage = 'URL copied.';
            }
        },

        async doJsonRequest(request) {
            this.backendStatus = 0;
            this.backendMessage = '';
            this.requestInProgress = true;

            try {
                return await request;
            } catch (error) {
                this.backendStatus = 400;
                this.backendMessage = 'Connection failed. Try restarting Warp Journal.';
                console.error(error);
                return null;
            } finally {
                this.requestInProgress = false;
            }
        },

        // page and filter the warp history for display
        pageWarpHistory() {
            // first, turn our filters into lists
            const filters = {};
            for (const [ column, filter ] of Object.entries(this.columnFilters)) {
                const formatter = filter.__formatter ?? ((key) => key);
                filters[column] = [];
                for (const [ key, enabled ] of Object.entries(filter)) {
                    if (key == '__formatter') {
                        continue;
                    }
                    if (enabled) {
                        filters[column].push(formatter(key));
                    }
                }
            }

            // then, create a filtered copy of the warp history
            filteredWarpHistory = this.warpHistory.filter((warp) => {
                let include = true;
                for (const [ column, permittedValues ] of Object.entries(filters)) {
                    if (!permittedValues.includes(warp[column])) {
                        include = false;
                        break;
                    }
                }
                return include;
            });

            // re-calculate last page based on filtered list
            this.warpHistoryLastPage = Math.max(0, Math.ceil(filteredWarpHistory.length / this.warpHistoryPageSize) - 1);
            if (this.warpHistoryPage > this.warpHistoryLastPage) {
                this.warpHistoryPage = this.warpHistoryLastPage;
            }

            // grab the slice that is our current page
            this.pagedWarpHistory = filteredWarpHistory.slice(
                this.warpHistoryPage * this.warpHistoryPageSize,
                this.warpHistoryPage * this.warpHistoryPageSize + this.warpHistoryPageSize
            );

            // add empty entries to prevent visual jumps if length < pageSize
            while (this.pagedWarpHistory.length < this.warpHistoryPageSize) {
                this.pagedWarpHistory.push({
                    name: '–',
                    rarityText: '–',
                    type: '–',
                    bannerTypeName: '–',
                    time: '–'
                });
            }
        },

        firstPage() {
            this.warpHistoryPage = 0;
            this.pageWarpHistory();
        },

        previousPage() {
            this.warpHistoryPage = Math.max(0, this.warpHistoryPage - 1);
            this.pageWarpHistory();
        },

        nextPage() {
            this.warpHistoryPage = Math.min(this.warpHistoryLastPage, this.warpHistoryPage + 1);
            this.pageWarpHistory();
        },

        lastPage() {
            this.warpHistoryPage = this.warpHistoryLastPage;
            this.pageWarpHistory();
        },

        toggleColumnSettings(event, column) {
            event.stopPropagation();
            this.columnSettingsOpen[column] = !this.columnSettingsOpen[column];

            // hide uid selector if it's open
            if (this.uidSelectorOpen) {
                this.uidSelectorOpen = false;
            }

            // hide any other open settings
            if (this.columnSettingsOpen[column]) {
                for (const [ key, isOpen ] of Object.entries(this.columnSettingsOpen)) {
                    if (key != column && isOpen) {
                        this.columnSettingsOpen[key] = false;
                    }
                }
            }
        },

        // helper method, because dynamically setting x-model inside x-for does not seem to work (?)
        bannerTypeFilterChange(event, bannerType) {
            this.columnFilters.bannerType[`_${bannerType}`] = event.target.checked;
        },

        toggleUIDSelector(event) {
            event.stopPropagation();
            this.uidSelectorOpen = !this.uidSelectorOpen;

            // hide any open column settings
            for (const [ key, isOpen ] of Object.entries(this.columnSettingsOpen)) {
                if (isOpen) {
                    this.columnSettingsOpen[key] = false;
                }
            }
        },

        selectUID(uid) {
            this.$refs.uidSelector._x_model.set(uid);
            this.uidSelectorOpen = false;

            this.statistics = this.uidData[uid].statistics;
            this.pity = this.uidData[uid].pity;
            this.lowPity = this.uidData[uid].lowPity;
            this.warpHistory = this.uidData[uid].warpHistory;
            this.totalWarps = this.uidData[uid].totalWarps;

            this.warpHistoryPage = 0;
            this.pageWarpHistory();
        }
    }));
});

// background stars
(() => {
    function rand(min, max) {
        return (Math.random() * (min + max)) - min;
    }

    const fragments = [
        new DocumentFragment(),
        new DocumentFragment(),
        new DocumentFragment(),
        new DocumentFragment()
    ];
    for (let i = 0; i < 500; i++) {
        const star = document.createElement('span');
        star.classList.add('bg-star');

        const x = rand(2, 100);
        let y = rand(5, 200 - 0.02 * ((x - 49) ** 2));
        y = y ** 1.2;
        star.style.left = `${x}%`;
        star.style.top = `${y}px`;

        const size = Math.random();
        if (size < 0.5) {
            star.classList.add('s1');
            fragments[Math.random() < 0.5 ? 0 : 1].append(star);
        } else if (size < 0.8) {
            star.classList.add('s2');
            fragments[Math.random() < 0.5 ? 1 : 2].append(star);
        } else if (size < 0.97) {
            star.classList.add('s3');
            fragments[Math.random() < 0.75 ? 2 : 3].append(star);
        } else {
            star.classList.add('s4');
            fragments[3].append(star);
        }
    }

    const starsContainer1 = document.querySelector('#bg-stars > .c1');
    const starsContainer2 = document.querySelector('#bg-stars > .c2');
    const starsContainer3 = document.querySelector('#bg-stars > .c3');
    const starsContainer4 = document.querySelector('#bg-stars > .c4');

    starsContainer1.appendChild(fragments[0]);
    starsContainer2.appendChild(fragments[1]);
    starsContainer3.appendChild(fragments[2]);
    starsContainer4.appendChild(fragments[3]);

    document.addEventListener('scroll', (event) => {
        starsContainer1.style.transform = `translateY(-${Math.floor(window.scrollY / 20)}px)`;
        starsContainer2.style.transform = `translateY(-${Math.floor(window.scrollY / 10)}px)`;
        starsContainer3.style.transform = `translateY(-${Math.floor(window.scrollY / 7)}px)`;
        starsContainer4.style.transform = `translateY(-${Math.floor(window.scrollY / 5)}px)`;
    });
})();

// ===== STORYWEAVER BOOK APP - PAGE TURN LOGIC + API =====

class StoryBook {
    constructor() {
        this.pages = ['cover', 'setup', 'story', 'gallery'];
        this.currentPage = 0;
        this.isAnimating = false;
        this.story = null;
        this.favorites = JSON.parse(localStorage.getItem('storyFavorites') || '[]');

        this.init();
    }

    init() {
        this.cacheDOMElements();
        this.bindEvents();
        this.updateUI();
        this.loadFavorites();
    }

    cacheDOMElements() {
        this.book = document.getElementById('book');
        this.pageElements = document.querySelectorAll('.book-page');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.pageIndicator = document.getElementById('pageIndicator');
        this.openBookBtn = document.getElementById('openBookBtn');
        this.generateBtn = document.getElementById('generateBtn');
        this.storyTitle = document.getElementById('storyTitle');
        this.storyMeta = document.getElementById('storyMeta');
        this.storyText = document.getElementById('storyText');
        this.storyIllustrations = document.getElementById('storyIllustrations');
        this.favoriteBtn = document.getElementById('favoriteBtn');
        this.newStoryBtn = document.getElementById('newStoryBtn');
        this.bookShelf = document.getElementById('bookShelf');
    }

    bindEvents() {
        this.openBookBtn.addEventListener('click', () => this.nextPage());
        this.prevBtn.addEventListener('click', () => this.prevPage());
        this.nextBtn.addEventListener('click', () => this.nextPage());
        this.generateBtn.addEventListener('click', () => this.generateStory());
        this.favoriteBtn.addEventListener('click', () => this.toggleFavorite());
        this.newStoryBtn.addEventListener('click', () => this.goToPage(1));

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') this.nextPage();
            if (e.key === 'ArrowLeft') this.prevPage();
        });

        let touchStartX = 0;
        this.book.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        this.book.addEventListener('touchend', (e) => {
            const diff = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) this.nextPage();
                else this.prevPage();
            }
        }, { passive: true });

        this.bindOptionSelectors();
    }

    bindOptionSelectors() {
        document.querySelectorAll('.age-option').forEach(el => {
            el.addEventListener('click', () => {
                document.querySelectorAll('.age-option').forEach(o => o.classList.remove('selected'));
                el.classList.add('selected');
            });
        });

        document.querySelectorAll('.moral-option').forEach(el => {
            el.addEventListener('click', () => {
                document.querySelectorAll('.moral-option').forEach(o => o.classList.remove('selected'));
                el.classList.add('selected');
            });
        });

        document.querySelectorAll('.character-option').forEach(el => {
            el.addEventListener('click', () => {
                document.querySelectorAll('.character-option').forEach(o => o.classList.remove('selected'));
                el.classList.add('selected');
                this.updateGenderVisibility();
            });
        });

        document.querySelectorAll('.gender-option').forEach(el => {
            el.addEventListener('click', () => {
                document.querySelectorAll('.gender-option').forEach(o => o.classList.remove('selected'));
                el.classList.add('selected');
            });
        });

        this.updateGenderVisibility();
    }

    updateGenderVisibility() {
        const character = document.querySelector('.character-option.selected')?.dataset.value || 'animal';
        const genderSection = document.getElementById('genderSection');
        const humanLike = ['princess', 'prince', 'superhero', 'dragon', 'robot', 'fairy', 'knight', 'mermaid', 'pirate', 'wizard'];
        if (humanLike.includes(character)) {
            genderSection.style.display = 'block';
        } else {
            genderSection.style.display = 'none';
            document.querySelectorAll('.gender-option').forEach(o => o.classList.remove('selected'));
        }
    }

    getSelectedOptions() {
        const age = document.querySelector('.age-option.selected')?.dataset.value || '5-6';
        const moral = document.querySelector('.moral-option.selected')?.dataset.value || 'sharing is caring';
        const character = document.querySelector('.character-option.selected')?.dataset.value || 'animal';
        const gender = document.querySelector('.gender-option.selected')?.dataset.value || '';
        return { age, moral, character, gender };
    }

    async generateStory() {
        const options = this.getSelectedOptions();
        this.setLoading(true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    age: options.age,
                    moralLesson: options.moral,
                    character: options.character,
                    gender: options.gender
                })
            });

            if (!response.ok) throw new Error('Failed to generate story');

            const data = await response.json();
            this.story = data.story;
            this.displayStory();
            this.goToPage(2);
        } catch (error) {
            console.error('Story generation failed:', error);
            this.story = this.getMockStory(options);
            this.displayStory();
            this.goToPage(2);
        } finally {
            this.setLoading(false);
        }
    }

    getMockStory(options) {
        const titles = {
            animal: 'The Brave Little Animal',
            princess: 'The Princess and the Magic Garden',
            prince: 'The Prince and the Golden Lesson'
        };
        return {
            id: 'mock-' + Date.now(),
            title: titles[options.character] || 'The Story',
            age: options.age,
            moralLesson: options.moral,
            character: options.character,
            storyText: `Once upon a time, in a magical forest filled with wonder, there lived a curious ${options.character} who wanted to learn about ${options.moral}.\n\nEvery day, the ${options.character} would explore the forest, meeting new friends and discovering new things. One day, they found a lost little bird who couldn't find its way home.\n\nThe ${options.character} knew that ${options.moral} was important, so they helped the bird find its family. Along the way, they learned that helping others makes everyone happy.\n\nFrom that day on, the ${options.character} became known as the kindest creature in the forest, and all the animals loved them very much.\n\nThe End.`,
            imageUrls: [
                'https://via.placeholder.com/400x300/7A9E7E/FFFFFF?text=Story+1',
                'https://via.placeholder.com/400x300/D47B4E/FFFFFF?text=Story+2',
                'https://via.placeholder.com/400x300/5A7BA8/FFFFFF?text=Story+3'
            ],
            favorite: false
        };
    }

    displayStory() {
        if (!this.story) return;

        this.storyTitle.textContent = this.story.title;
        this.storyMeta.textContent = `A tale of ${this.story.moralLesson} for ages ${this.story.age}`;

        const paragraphs = this.story.storyText.split('\n\n');
        this.storyText.innerHTML = paragraphs.map((p, i) =>
            `<p>${p}</p>`
        ).join('');

        this.storyIllustrations.innerHTML = '';
        this.story.imageUrls.forEach((url, i) => {
            const img = document.createElement('img');
            img.src = url;
            img.alt = `Illustration ${i + 1}`;
            img.className = 'illustration';
            this.storyIllustrations.appendChild(img);
        });

        this.updateFavoriteBtn();
    }

    toggleFavorite() {
        if (!this.story) return;

        this.story.favorite = !this.story.favorite;
        this.updateFavoriteBtn();

        const index = this.favorites.findIndex(s => s.id === this.story.id);
        if (this.story.favorite && index === -1) {
            this.favorites.push(this.story);
        } else if (!this.story.favorite && index !== -1) {
            this.favorites.splice(index, 1);
        }

        localStorage.setItem('storyFavorites', JSON.stringify(this.favorites));
        this.loadFavorites();
    }

    updateFavoriteBtn() {
        if (this.story?.favorite) {
            this.favoriteBtn.textContent = '❤️ Saved';
            this.favoriteBtn.classList.add('favorited');
        } else {
            this.favoriteBtn.textContent = '🤍 Save';
            this.favoriteBtn.classList.remove('favorited');
        }
    }

    loadFavorites() {
        if (this.favorites.length === 0) {
            this.bookShelf.innerHTML = '<p style="color: var(--ink-faint); font-family: var(--font-hand); font-size: var(--fs-lg); width: 100%; text-align: center;">Your story collection is empty. Create some stories!</p>';
            return;
        }

        this.bookShelf.innerHTML = '';
        this.favorites.forEach(story => {
            const spine = document.createElement('div');
            spine.className = 'book-spine-item';
            spine.textContent = story.title;
            spine.addEventListener('click', () => {
                this.story = story;
                this.displayStory();
                this.goToPage(2);
            });
            this.bookShelf.appendChild(spine);
        });
    }

    goToPage(index) {
        if (this.isAnimating || index < 0 || index >= this.pages.length) return;
        this.isAnimating = true;

        const currentPageEl = this.pageElements[this.currentPage];
        const nextPageEl = this.pageElements[index];

        currentPageEl.classList.add('turning');

        setTimeout(() => {
            currentPageEl.classList.remove('active', 'turning');
            nextPageEl.classList.add('active');
            this.currentPage = index;
            this.updateUI();
            this.isAnimating = false;
        }, 600);
    }

    nextPage() {
        this.goToPage(this.currentPage + 1);
    }

    prevPage() {
        this.goToPage(this.currentPage - 1);
    }

    updateUI() {
        this.prevBtn.disabled = this.currentPage === 0;
        this.nextBtn.disabled = this.currentPage === this.pages.length - 1;
        this.pageIndicator.textContent = `${this.currentPage + 1} / ${this.pages.length}`;
    }

    setLoading(loading) {
        this.generateBtn.disabled = loading;
        this.generateBtn.textContent = loading ? '✨ Creating...' : '✨ Generate Story';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new StoryBook();
});
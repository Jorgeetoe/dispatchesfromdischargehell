/* ============================================
   DISPATCHES FROM DISCHARGE HELL
   Modular JavaScript Architecture
   ============================================ */

(function() {
  'use strict';

  /* --- Theme Module --- */
  const ThemeManager = {
    THEME_KEY: 'dispatch-theme',

    getPreferredTheme() {
      const stored = localStorage.getItem(this.THEME_KEY);
      if (stored) return stored;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    },

    setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem(this.THEME_KEY, theme);
      this.updateToggleButton(theme);
    },

    updateToggleButton(theme) {
      const btn = document.querySelector('.theme-toggle');
      if (btn) {
        btn.textContent = theme === 'dark' ? '☀️' : '🌙';
        btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      }
    },

    toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || this.getPreferredTheme();
      const next = current === 'dark' ? 'light' : 'dark';
      this.setTheme(next);
    },

    init() {
      const preferred = this.getPreferredTheme();
      this.setTheme(preferred);

      const toggleBtn = document.querySelector('.theme-toggle');
      if (toggleBtn) {
        toggleBtn.addEventListener('click', () => this.toggleTheme());
      }

      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(this.THEME_KEY)) {
          this.setTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  };

  /* --- Read Time Module --- */
  const ReadTimeCalculator = {
    calculate() {
      const content = document.querySelector('.article-content');
      if (!content) return;

      const text = content.innerText || content.textContent;
      const wordCount = text.trim().split(/\s+/).length;
      const readTime = Math.ceil(wordCount / 238);
      const readTimeText = readTime === 1 ? '1 min read' : `${readTime} min read`;

      const postMeta = document.querySelector('article .post-meta');
      if (postMeta) {
        const separator = document.createTextNode(' · ');
        const readTimeSpan = document.createElement('span');
        readTimeSpan.className = 'read-time';
        readTimeSpan.textContent = readTimeText;

        postMeta.appendChild(separator);
        postMeta.appendChild(readTimeSpan);
      }
    },

    init() {
      this.calculate();
    }
  };

  /* --- Progress Tracker Module --- */
  const ProgressTracker = {
    bar: null,
    ticking: false,

    createProgressBar() {
      const bar = document.createElement('div');
      bar.className = 'progress-bar';
      const fill = document.createElement('div');
      fill.className = 'progress-bar-fill';
      bar.appendChild(fill);
      document.body.insertBefore(bar, document.body.firstChild);
      return fill;
    },

    updateProgress() {
      if (!this.bar) return;

      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = scrollHeight > 0 ? (window.scrollY / scrollHeight) * 100 : 0;
      this.bar.style.width = Math.max(0, Math.min(100, progress)) + '%';
    },

    onScroll() {
      if (!this.ticking) {
        requestAnimationFrame(() => this.updateProgress());
        this.ticking = true;
        setTimeout(() => {
          this.ticking = false;
        }, 100);
      }
    },

    init() {
      if (!document.querySelector('.article-content')) return;

      this.bar = this.createProgressBar();
      this.updateProgress();

      window.addEventListener('scroll', () => this.onScroll());
    }
  };

  /* --- Post Search Module --- */
  const PostSearch = {
    index: [],
    input: null,
    resultsContainer: null,

    buildIndex() {
      const postList = document.querySelector('.post-list');
      if (!postList) return;

      postList.querySelectorAll('li').forEach(li => {
        const titleEl = li.querySelector('.post-title a');
        const excerptEl = li.querySelector('.post-excerpt');
        const categoryEl = li.querySelector('.category');

        if (titleEl) {
          const title = titleEl.textContent || '';
          const excerpt = excerptEl ? (excerptEl.textContent || '') : '';
          const category = categoryEl ? (categoryEl.textContent || '') : '';
          const url = titleEl.href || '';

          this.index.push({
            title: title.toLowerCase(),
            excerpt: excerpt.toLowerCase(),
            category: category.toLowerCase(),
            url,
            originalTitle: title,
            originalExcerpt: excerpt,
            originalCategory: category
          });
        }
      });
    },

    renderSearchUI() {
      const h1 = document.querySelector('h1');
      if (!h1) return;

      const searchHTML = `
        <div class="search-box">
          <input type="text" id="search-input" placeholder="Search posts..." aria-label="Search blog posts">
          <ul id="search-results" class="search-results hidden"></ul>
        </div>
      `;
      h1.insertAdjacentHTML('afterend', searchHTML);

      this.input = document.getElementById('search-input');
      this.resultsContainer = document.getElementById('search-results');
    },

    search(query) {
      if (!this.resultsContainer) return;

      const q = query.toLowerCase().trim();

      if (!q) {
        this.resultsContainer.classList.add('hidden');
        return;
      }

      const matches = this.index.filter(post =>
        post.title.includes(q) ||
        post.excerpt.includes(q) ||
        post.category.includes(q)
      );

      this.resultsContainer.innerHTML = matches.map(m => `
        <li><a href="${m.url}">${m.originalTitle}</a></li>
      `).join('');

      this.resultsContainer.classList.toggle('hidden', matches.length === 0);
    },

    attachHandlers() {
      if (this.input) {
        this.input.addEventListener('input', (e) => this.search(e.target.value));
      }
    },

    init() {
      this.buildIndex();
      if (this.index.length === 0) return;

      this.renderSearchUI();
      this.attachHandlers();
    }
  };

  /* --- Category Filter Module --- */
  const CategoryFilter = {
    activeFilters: new Set(),

    countPostsByCategory() {
      const postList = document.querySelector('.post-list');
      if (!postList) return {};

      const counts = {
        'all': postList.querySelectorAll('li').length,
        'dispatches': 0,
        'field-notes': 0,
        'the-machine': 0,
        'case-files': 0,
        'persona': 0
      };

      postList.querySelectorAll('li').forEach(li => {
        const categoryEl = li.querySelector('.category');
        if (categoryEl) {
          const cat = categoryEl.textContent.toLowerCase().replace(/ /g, '-');
          if (counts[cat] !== undefined) counts[cat]++;
        }
      });

      return counts;
    },

    renderFilterUI() {
      const h1 = document.querySelector('h1');
      if (!h1) return;

      const categories = ['Dispatches', 'Field Notes', 'The Machine', 'Case Files', 'Persona'];
      const counts = this.countPostsByCategory();

      const filterHTML = `
        <div class="filter-controls">
          <button class="filter-button active" data-filter="all">All (${counts.all})</button>
          ${categories.map(cat => {
            const key = cat.toLowerCase().replace(/ /g, '-');
            return `<button class="filter-button" data-filter="${key}">${cat} (${counts[key]})</button>`;
          }).join('')}
        </div>
      `;

      const searchBox = h1.nextElementSibling;
      if (searchBox && searchBox.classList.contains('search-box')) {
        searchBox.insertAdjacentHTML('afterend', filterHTML);
      } else {
        h1.insertAdjacentHTML('afterend', filterHTML);
      }
    },

    applyFilter(btn) {
      document.querySelectorAll('.filter-button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      const postList = document.querySelector('.post-list');

      if (!postList) return;

      postList.querySelectorAll('li').forEach(li => {
        const isMatch = filter === 'all' || (function() {
          const categoryEl = li.querySelector('.category');
          const categoryText = categoryEl ? categoryEl.textContent.toLowerCase().replace(/ /g, '-') : '';
          return categoryText === filter;
        })();

        li.style.opacity = '0.5';
        li.style.transition = 'opacity 0.15s ease';

        setTimeout(() => {
          li.style.display = isMatch ? '' : 'none';
          li.style.opacity = '1';
        }, 75);
      });
    },

    attachHandlers() {
      document.querySelectorAll('.filter-button').forEach(btn => {
        btn.addEventListener('click', () => this.applyFilter(btn));
      });
    },

    init() {
      const postList = document.querySelector('.post-list');
      if (!postList) return;

      this.renderFilterUI();
      this.attachHandlers();
    }
  };

  /* --- Table of Contents Module --- */
  const TableOfContents = {
    MIN_WORD_COUNT: 1500,

    init() {
      const content = document.querySelector('.article-content');
      if (!content) return;

      // Count words
      const text = content.innerText || content.textContent;
      const wordCount = text.trim().split(/\s+/).length;

      if (wordCount < this.MIN_WORD_COUNT) return;

      // Find all h2 elements
      const headings = content.querySelectorAll('h2');
      if (headings.length === 0) return;

      // Generate TOC
      this.generateTOC(headings, content);
    },

    generateTOC(headings, content) {
      // Add IDs to headings if they don't have them
      headings.forEach((h, index) => {
        if (!h.id) {
          h.id = `heading-${index + 1}`;
        }
      });

      // Create TOC HTML
      const tocHTML = `
        <nav class="table-of-contents">
          <div class="toc-header">
            <button class="toc-toggle" aria-expanded="true" aria-label="Toggle table of contents">
              <span class="toc-title">Contents</span>
              <span class="toc-icon">−</span>
            </button>
          </div>
          <ol class="toc-list">
            ${Array.from(headings).map(h => `
              <li><a href="#${h.id}">${h.textContent}</a></li>
            `).join('')}
          </ol>
        </nav>
      `;

      // Insert before article content or after article header
      const articleHeader = document.querySelector('article header');
      if (articleHeader) {
        articleHeader.insertAdjacentHTML('afterend', tocHTML);
      } else {
        content.insertAdjacentHTML('beforebegin', tocHTML);
      }

      // Attach toggle handler
      const toggle = document.querySelector('.toc-toggle');
      const tocList = document.querySelector('.toc-list');
      if (toggle && tocList) {
        toggle.addEventListener('click', () => {
          const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
          toggle.setAttribute('aria-expanded', !isExpanded);
          tocList.classList.toggle('collapsed');
          toggle.querySelector('.toc-icon').textContent = isExpanded ? '+' : '−';
        });
      }
    }
  };

  /* --- Series Navigation Module --- */
  const SeriesNavigation = {
    // 25-part series index
    series: {
      1: { title: 'The Family Readiness Mismatch', url: '/blog/posts/2024-01-03-family-readiness-mismatch-part-1.html' },
      2: { title: 'The Payer-Driven Discharge Timeline', url: '/blog/posts/2024-01-06-payer-driven-discharge-timeline-part-2.html' },
      3: { title: 'The Ghost SNF', url: '/blog/posts/2024-01-09-ghost-snf-part-3.html' },
      4: { title: 'The DME Delivery Black Hole', url: '/blog/posts/2024-01-12-dme-delivery-black-hole-part-4.html' },
      5: { title: 'The Home Health Illusion', url: '/blog/posts/2024-01-15-home-health-illusion-part-5.html' },
      6: { title: 'The Faith-Function Tension', url: '/blog/posts/2024-01-18-faith-function-tension-part-6.html' },
      7: { title: 'Funny How That Works', url: '/blog/posts/2024-01-21-funny-how-that-works-part-7.html' },
      8: { title: 'The Complexity-Admission Mismatch', url: '/blog/posts/2024-01-24-complexity-admission-mismatch-part-8.html' },
      9: { title: 'The Difficult Conversation Industrial Complex', url: '/blog/posts/2024-01-27-difficult-conversation-industrial-complex-part-9.html' },
      10: { title: 'Perverse Incentives by Design', url: '/blog/posts/2024-01-30-perverse-incentives-by-design-part-10.html' },
      11: { title: 'It Depends on Who Shows Up', url: '/blog/posts/2024-02-02-family-presence-variable-part-11.html' },
      12: { title: 'Not Our Problem Anymore', url: '/blog/posts/2024-02-05-hot-potato-protocol-part-12.html' },
      13: { title: "We Don't Do Out-of-Area", url: '/blog/posts/2024-02-11-we-dont-do-out-of-area-part-13.html' },
      14: { title: 'I Already Called Them', url: '/blog/posts/2024-02-08-i-already-called-them-part-14.html' }
    },

    init() {
      const article = document.querySelector('article');
      if (!article) return;

      const partNum = parseInt(article.dataset.seriesPart);
      if (!partNum || !this.series[partNum]) return;

      this.renderSeriesNav(article, partNum);
    },

    renderSeriesNav(article, partNum) {
      const prev = partNum > 1 ? this.series[partNum - 1] : null;
      const next = partNum < 14 ? this.series[partNum + 1] : null;

      let navHTML = `
        <div class="series-nav">
          <div class="series-info">
            <span class="series-badge">Series: Part ${partNum} of 25</span>
            <a href="/blog/posts/2024-01-01-dispatches-from-discharge-hell-25-part-series.html" class="series-index-link">View Series Index →</a>
          </div>
          <div class="series-steps">
      `;

      if (prev) {
        navHTML += `
          <a href="${prev.url}" class="series-step prev">
            <span class="series-step-label">← Previous Part</span>
            <span class="series-step-title">${prev.title}</span>
          </a>
        `;
      }

      if (next) {
        navHTML += `
          <a href="${next.url}" class="series-step next">
            <span class="series-step-label">Next Part →</span>
            <span class="series-step-title">${next.title}</span>
          </a>
        `;
      }

      navHTML += `
          </div>
        </div>
      `;

      const articleHeader = article.querySelector('header');
      if (articleHeader) {
        articleHeader.insertAdjacentHTML('afterend', navHTML);
      }
    }
  };

  /* --- Social Sharing Module --- */
  const SocialSharing = {
    init() {
      const article = document.querySelector('article');
      if (!article) return;

      const h1 = article.querySelector('h1');
      if (!h1) return;

      const pageURL = window.location.href;
      const pageTitle = h1.textContent.trim();

      this.renderShareButtons(h1, pageURL, pageTitle);
    },

    renderShareButtons(h1, url, title) {
      const shareHTML = `
        <div class="share-buttons">
          <span class="share-label">Share</span>
          <button class="share-btn share-copy" data-url="${url}" title="Copy link to clipboard" aria-label="Copy link">
            <span class="share-icon">🔗</span>
            <span class="share-text">Copy</span>
          </button>
          <a href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}"
             class="share-btn share-linkedin" target="_blank" rel="noopener"
             title="Share on LinkedIn" aria-label="Share on LinkedIn">
            <span class="share-icon">in</span>
            <span class="share-text">LinkedIn</span>
          </a>
          <a href="https://x.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}&via=JorgeArenivar"
             class="share-btn share-twitter" target="_blank" rel="noopener"
             title="Share on X" aria-label="Share on X">
            <span class="share-icon">𝕏</span>
            <span class="share-text">X</span>
          </a>
        </div>
      `;

      const header = h1.closest('header');
      if (header) {
        header.insertAdjacentHTML('afterend', shareHTML);
      } else {
        h1.insertAdjacentHTML('afterend', shareHTML);
      }

      // Attach copy handler
      const copyBtn = document.querySelector('.share-copy');
      if (copyBtn) {
        copyBtn.addEventListener('click', () => this.copyToClipboard(copyBtn, url));
      }
    },

    copyToClipboard(btn, url) {
      navigator.clipboard.writeText(url).then(() => {
        const originalText = btn.querySelector('.share-text').textContent;
        btn.querySelector('.share-text').textContent = 'Copied!';
        btn.classList.add('copied');

        setTimeout(() => {
          btn.querySelector('.share-text').textContent = originalText;
          btn.classList.remove('copied');
        }, 2000);
      }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = url;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        const originalText = btn.querySelector('.share-text').textContent;
        btn.querySelector('.share-text').textContent = 'Copied!';
        btn.classList.add('copied');

        setTimeout(() => {
          btn.querySelector('.share-text').textContent = originalText;
          btn.classList.remove('copied');
        }, 2000);
      });
    }
  };

  /* --- Related Posts Module --- */
  const RelatedPosts = {
    init() {
      const article = document.querySelector('article');
      if (!article) return;

      const dataAttr = article.dataset.relatedPosts;
      if (!dataAttr) return;

      const urls = dataAttr.split(',').map(u => u.trim()).filter(u => u);
      if (urls.length === 0) return;

      const container = document.querySelector('.newsletter-cta');
      if (!container) return;

      this.renderRelatedPosts(container, urls);
    },

    renderRelatedPosts(container, urls) {
      const relatedHTML = `
        <section class="related-posts">
          <h3>Related Dispatches</h3>
          <div class="related-posts-grid">
            ${urls.map(url => `
              <a href="${url}" class="related-post-card">
                <span>Loading...</span>
              </a>
            `).join('')}
          </div>
        </section>
      `;
      container.insertAdjacentHTML('beforebegin', relatedHTML);
    }
  };

  /* --- Back-to-Top Button Module --- */
  const BackToTop = {
    button: null,
    threshold: window.innerHeight,

    init() {
      this.createButton();
      this.attachHandlers();
    },

    createButton() {
      this.button = document.createElement('button');
      this.button.className = 'back-to-top';
      this.button.setAttribute('aria-label', 'Back to top');
      this.button.innerHTML = '↑';
      this.button.style.display = 'none';
      document.body.appendChild(this.button);
    },

    attachHandlers() {
      if (!this.button) return;

      window.addEventListener('scroll', () => this.toggleVisibility());
      this.button.addEventListener('click', () => this.scrollToTop());
    },

    toggleVisibility() {
      if (!this.button) return;
      const shouldShow = window.scrollY > this.threshold;
      this.button.style.display = shouldShow ? 'flex' : 'none';
    },

    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };

  /* --- Mobile Navigation Module --- */
  const MobileNav = {
    init() {
      const hamburger = document.querySelector('.hamburger');
      const nav = document.querySelector('nav');

      if (!hamburger || !nav) return;

      hamburger.addEventListener('click', () => {
        nav.classList.toggle('hidden');
      });

      // Close menu when link is clicked
      nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          nav.classList.add('hidden');
        });
      });
    }
  };

  /* --- Initialize All Modules --- */
  document.addEventListener('DOMContentLoaded', function() {
    ThemeManager.init();
    MobileNav.init();
    BackToTop.init();
    ReadTimeCalculator.init();
    ProgressTracker.init();
    PostSearch.init();
    CategoryFilter.init();
    TableOfContents.init();
    SeriesNavigation.init();
    SocialSharing.init();
    RelatedPosts.init();
  });
})();

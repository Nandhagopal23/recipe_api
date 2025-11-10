let currentPage = 1;
let currentLimit = 15;
let totalPages = 1;
let currentFilters = {};

// Load initial data
document.addEventListener('DOMContentLoaded', function() {
    loadRecipes();
});

async function loadRecipes(page = 1, limit = currentLimit) {
    try {
        const response = await fetch(`/api/recipes?page=${page}&limit=${limit}`);
        const data = await response.json();
        
        currentPage = data.page;
        currentLimit = data.limit;
        totalPages = Math.ceil(data.total / data.limit);
        
        updatePagination();
        renderRecipes(data.data);
        
    } catch (error) {
        console.error('Error loading recipes:', error);
    }
}

async function searchRecipes(filters = {}) {
    try {
        const params = new URLSearchParams();
        
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                params.append(key, filters[key]);
            }
        });
        
        const response = await fetch(`/api/recipes/search?${params}`);
        const data = await response.json();
        
        renderRecipes(data.data);
        updatePaginationForSearch(data.data.length);
        
    } catch (error) {
        console.error('Error searching recipes:', error);
    }
}

function renderRecipes(recipes) {
    const tbody = document.getElementById('recipesBody');
    const noResults = document.getElementById('noResults');
    
    if (recipes.length === 0) {
        tbody.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }
    
    noResults.classList.add('hidden');
    
    tbody.innerHTML = recipes.map(recipe => `
        <tr onclick="showRecipeDetail(${recipe.id})">
            <td class="title-cell" title="${recipe.title}">${recipe.title}</td>
            <td>${recipe.cuisine || 'N/A'}</td>
            <td>${renderStarRating(recipe.rating)}</td>
            <td>${recipe.total_time ? recipe.total_time + ' mins' : 'N/A'}</td>
            <td>${recipe.serves || 'N/A'}</td>
        </tr>
    `).join('');
}

function renderStarRating(rating) {
    if (!rating) return 'N/A';
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let stars = '';
    
    // Full stars
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star star-rating"></i>';
    }
    
    // Half star
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt star-rating"></i>';
    }
    
    // Empty stars
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star star-rating"></i>';
    }
    
    return stars + ` (${rating})`;
}

async function showRecipeDetail(recipeId) {
    try {
        // In a real app, you might want a separate endpoint for single recipe
        // For now, we'll use the search endpoint or get all and filter
        const response = await fetch(`/api/recipes/search?title=&rating=`);
        const data = await response.json();
        
        const recipe = data.data.find(r => r.id === recipeId);
        
        if (recipe) {
            renderRecipeDetail(recipe);
            openDrawer();
        }
    } catch (error) {
        console.error('Error loading recipe detail:', error);
    }
}

function renderRecipeDetail(recipe) {
    const drawerContent = document.getElementById('drawerContent');
    
    drawerContent.innerHTML = `
        <div class="drawer-header">
            <h2>${recipe.title}</h2>
            <div class="cuisine">${recipe.cuisine || 'N/A'}</div>
        </div>
        
        <div class="detail-section">
            <h3>Description</h3>
            <p>${recipe.description || 'No description available.'}</p>
        </div>
        
        <div class="detail-section">
            <h3>
                Total Time: ${recipe.total_time ? recipe.total_time + ' minutes' : 'N/A'}
                <button class="expand-btn" onclick="toggleTimeDetails(this)">
                    <i class="fas fa-chevron-down"></i>
                </button>
            </h3>
            <div class="time-details hidden">
                <p><strong>Prep Time:</strong> ${recipe.prep_time ? recipe.prep_time + ' minutes' : 'N/A'}</p>
                <p><strong>Cook Time:</strong> ${recipe.cook_time ? recipe.cook_time + ' minutes' : 'N/A'}</p>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Nutrition</h3>
            ${renderNutrientsTable(recipe.nutrients)}
        </div>
        
        ${recipe.url ? `<div class="detail-section">
            <h3>Source</h3>
            <a href="${recipe.url}" target="_blank">View Original Recipe</a>
        </div>` : ''}
    `;
}

function renderNutrientsTable(nutrients) {
    if (!nutrients || Object.keys(nutrients).length === 0) {
        return '<p>No nutrition information available.</p>';
    }
    
    const nutrientFields = [
        'calories', 'carbohydrateContent', 'cholesterolContent', 
        'fiberContent', 'proteinContent', 'saturatedFatContent',
        'sodiumContent', 'sugarContent', 'fatContent'
    ];
    
    const rows = nutrientFields.map(field => {
        if (nutrients[field]) {
            return `
                <tr>
                    <td><strong>${formatNutrientName(field)}</strong></td>
                    <td>${nutrients[field]}</td>
                </tr>
            `;
        }
        return '';
    }).join('');
    
    return `
        <table class="nutrients-table">
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

function formatNutrientName(name) {
    const names = {
        calories: 'Calories',
        carbohydrateContent: 'Carbohydrates',
        cholesterolContent: 'Cholesterol',
        fiberContent: 'Fiber',
        proteinContent: 'Protein',
        saturatedFatContent: 'Saturated Fat',
        sodiumContent: 'Sodium',
        sugarContent: 'Sugar',
        fatContent: 'Fat'
    };
    
    return names[name] || name;
}

function toggleTimeDetails(button) {
    const timeDetails = button.parentElement.nextElementSibling;
    const icon = button.querySelector('i');
    
    timeDetails.classList.toggle('hidden');
    icon.classList.toggle('fa-chevron-down');
    icon.classList.toggle('fa-chevron-up');
}

function openDrawer() {
    document.getElementById('detailDrawer').classList.add('open');
}

function closeDrawer() {
    document.getElementById('detailDrawer').classList.remove('open');
}

function applyFilters() {
    currentFilters = {
        title: document.getElementById('titleFilter').value,
        cuisine: document.getElementById('cuisineFilter').value,
        rating: document.getElementById('ratingFilter').value,
        calories: document.getElementById('caloriesFilter').value,
        total_time: document.getElementById('timeFilter').value
    };
    
    searchRecipes(currentFilters);
}

function clearFilters() {
    document.getElementById('titleFilter').value = '';
    document.getElementById('cuisineFilter').value = '';
    document.getElementById('ratingFilter').value = '';
    document.getElementById('caloriesFilter').value = '';
    document.getElementById('timeFilter').value = '';
    
    currentFilters = {};
    currentPage = 1;
    loadRecipes();
}

function changePage(direction) {
    const newPage = currentPage + direction;
    
    if (newPage >= 1 && newPage <= totalPages) {
        if (Object.keys(currentFilters).length > 0) {
            // For now, with filters we don't have proper pagination
            // In a real app, you'd modify the search to include pagination
            alert('Pagination with active filters is not implemented in this demo');
        } else {
            loadRecipes(newPage, currentLimit);
        }
    }
}

function changePerPage() {
    const newLimit = parseInt(document.getElementById('perPage').value);
    currentLimit = newLimit;
    currentPage = 1;
    
    if (Object.keys(currentFilters).length > 0) {
        searchRecipes(currentFilters);
    } else {
        loadRecipes(1, newLimit);
    }
}

function updatePagination() {
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
}

function updatePaginationForSearch(resultCount) {
    // For search results, we show all results on one page
    document.getElementById('pageInfo').textContent = `Search Results (${resultCount} found)`;
    document.getElementById('prevPage').disabled = true;
    document.getElementById('nextPage').disabled = true;
}

// Close drawer when clicking outside
document.addEventListener('click', function(event) {
    const drawer = document.getElementById('detailDrawer');
    if (event.target === drawer) {
        closeDrawer();
    }
});
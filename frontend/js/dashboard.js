// Additional dashboard-specific functions
async function loadPerformanceStats() {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (user.role === 'student') {
        try {
            // Load attendance stats
            const attendance = await apiCall('/attendance/my-attendance');
            const presentCount = attendance.filter(a => a.status === 'present').length;
            const totalClasses = attendance.length;
            const attendancePercentage = totalClasses > 0 ? (presentCount / totalClasses * 100).toFixed(2) : 0;
            
            // Load assignments
            const courses = await apiCall('/courses');
            let totalMarks = 0;
            let obtainedMarks = 0;
            
            // This is simplified - in real app, you'd fetch actual marks
            const statsHtml = `
                <div class="stat-item">
                    <strong>Attendance:</strong> ${attendancePercentage}% (${presentCount}/${totalClasses} days)
                </div>
                <div class="stat-item">
                    <strong>Courses Enrolled:</strong> ${courses.length}
                </div>
                <div class="stat-item">
                    <strong>Overall Progress:</strong> In Progress
                </div>
            `;
            
            document.getElementById('performance-stats').innerHTML = statsHtml;
        } catch (error) {
            document.getElementById('performance-stats').innerHTML = '<p>Failed to load statistics</p>';
        }
    } else if (user.role === 'teacher') {
        try {
            const courses = await apiCall('/courses');
            const statsHtml = `
                <div class="stat-item">
                    <strong>Courses Teaching:</strong> ${courses.length}
                </div>
                <div class="stat-item">
                    <strong>Total Students:</strong> Calculating...
                </div>
                <div class="stat-item">
                    <strong>Active Courses:</strong> ${courses.length}
                </div>
            `;
            document.getElementById('performance-stats').innerHTML = statsHtml;
        } catch (error) {
            document.getElementById('performance-stats').innerHTML = '<p>Failed to load statistics</p>';
        }
    }
}

// Load recent activities
async function loadRecentActivities() {
    const user = JSON.parse(localStorage.getItem('user'));
    
    // In a real application, you'd fetch activities from the backend
    const activitiesHtml = `
        <div class="activity-item">
            <i class="fas fa-check-circle"></i>
            <span>Logged in today</span>
        </div>
        <div class="activity-item">
            <i class="fas fa-book"></i>
            <span>Accessed the platform</span>
        </div>
    `;
    
    document.getElementById('recent-activities').innerHTML = activitiesHtml;
}

// Override the loadCourses function to also load stats
const originalLoadCourses = window.loadCourses;
window.loadCourses = async function() {
    await originalLoadCourses();
    await loadPerformanceStats();
    await loadRecentActivities();
}

// Add CSS for dashboard stats
const style = document.createElement('style');
style.textContent = `
    .stat-item {
        padding: 10px;
        margin: 5px 0;
        background: #f8f9fa;
        border-radius: 5px;
    }
    
    .activity-item {
        padding: 10px;
        margin: 5px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .activity-item i {
        color: #667eea;
    }
`;
document.head.appendChild(style);
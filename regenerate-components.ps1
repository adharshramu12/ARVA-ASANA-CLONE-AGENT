# Regenerate Clean Components Script
Write-Host "🧹 Cleaning old generated files..." -ForegroundColor Yellow

# Remove old files
Remove-Item -Force "$PSScriptRoot\frontend\generated\Home.jsx" -ErrorAction SilentlyContinue
Remove-Item -Force "$PSScriptRoot\frontend\generated\Projects.jsx" -ErrorAction SilentlyContinue
Remove-Item -Force "$PSScriptRoot\frontend\generated\Tasks.jsx" -ErrorAction SilentlyContinue

Write-Host "✅ Old files removed" -ForegroundColor Green

# Create Home.jsx
Write-Host "📝 Creating Home.jsx..." -ForegroundColor Cyan
$homeContent = @'
'use client';

export default function Home() {
  return (
    <div className="w-full h-screen overflow-auto bg-[#F7F7F7]">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <p className="text-sm text-gray-600 mb-2">Sunday, November 16</p>
          <h1 className="text-4xl font-light text-gray-900">Good morning, Bachu</h1>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">My week</h2>
          <div className="grid grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-bold">✓</div>
              <div>
                <div className="text-3xl font-semibold">0</div>
                <div className="text-sm text-gray-600">tasks completed</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">👥</div>
              <div>
                <div className="text-3xl font-semibold">0</div>
                <div className="text-sm text-gray-600">collaborators</div>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">My tasks</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded cursor-pointer">
              <input type="checkbox" className="w-5 h-5 rounded border-gray-300" />
              <div className="flex-1">
                <div className="font-medium">Draft project brief</div>
                <div className="text-sm text-gray-600">Cross-functional project plan</div>
              </div>
              <span className="text-sm text-gray-600">Today – Nov 18</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'@

Set-Content -Path "$PSScriptRoot\frontend\generated\Home.jsx" -Value $homeContent

# Create Projects.jsx
Write-Host "📝 Creating Projects.jsx..." -ForegroundColor Cyan
$projectsContent = @'
'use client';

export default function Projects() {
  return (
    <div className="w-full h-screen overflow-auto bg-[#F7F7F7]">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-medium text-gray-900">Browse projects</h1>
          <button className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium">
            + Create project
          </button>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded cursor-pointer">
            <div className="w-8 h-8 rounded bg-cyan-500 flex items-center justify-center text-white font-semibold">P</div>
            <div className="flex-1">
              <div className="font-medium">Cross-functional project plan</div>
              <div className="text-sm text-green-600">Joined</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'@

Set-Content -Path "$PSScriptRoot\frontend\generated\Projects.jsx" -Value $projectsContent

# Create Tasks.jsx
Write-Host "📝 Creating Tasks.jsx..." -ForegroundColor Cyan
$tasksContent = @'
'use client';

export default function Tasks() {
  return (
    <div className="w-full h-screen overflow-auto bg-[#F7F7F7]">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-medium text-gray-900 mb-2">My Tasks</h1>
          <p className="text-gray-600">Manage all your tasks in one place</p>
        </div>
        <div className="mb-6 border-b border-gray-200">
          <div className="flex gap-6">
            <button className="px-4 py-2 font-medium text-orange-600 border-b-2 border-orange-600">Upcoming</button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">Overdue</button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">Completed</button>
          </div>
        </div>
        <div className="space-y-3">
          <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5 rounded border-gray-300" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 mb-1">Draft project brief</h3>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-cyan-100 text-cyan-800">Cross-functional project plan</span>
                  <span>Due: Today – Nov 18</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'@

Set-Content -Path "$PSScriptRoot\frontend\generated\Tasks.jsx" -Value $tasksContent

Write-Host "`n✅ All components regenerated successfully!" -ForegroundColor Green
Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White

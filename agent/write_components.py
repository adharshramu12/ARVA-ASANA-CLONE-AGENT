import os

# Define the components
home_content = """'use client';

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
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-700">✓</div>
              <div>
                <div className="text-3xl font-semibold">0</div>
                <div className="text-sm text-gray-600">tasks completed</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700">📋</div>
              <div>
                <div className="text-3xl font-semibold">0</div>
                <div className="text-sm text-gray-600">tasks to do</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-medium mb-4">My tasks</h2>
          <p className="text-gray-500 text-center py-8">No tasks yet</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-medium mb-4">Projects</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="w-3 h-3 rounded-full bg-blue-500 mb-2"></div>
              <h3 className="font-medium">Sample Project</h3>
              <p className="text-sm text-gray-600 mt-1">0 tasks</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

tasks_content = """'use client';

export default function Tasks() {
  return (
    <div className="w-full h-screen overflow-auto bg-[#F7F7F7]">
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-light text-gray-900 mb-4">My Tasks</h1>
          
          <div className="flex gap-2 mb-6 border-b">
            <button className="px-4 py-2 text-blue-600 border-b-2 border-blue-600 font-medium">Upcoming</button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">Overdue</button>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">Completed</button>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium">Today</h2>
              <button className="text-blue-600 hover:text-blue-700 text-sm">+ Add task</button>
            </div>
            <p className="text-gray-500 text-center py-8">No tasks due today</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium">This Week</h2>
              <button className="text-blue-600 hover:text-blue-700 text-sm">+ Add task</button>
            </div>
            <p className="text-gray-500 text-center py-8">No upcoming tasks this week</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium">Later</h2>
              <button className="text-blue-600 hover:text-blue-700 text-sm">+ Add task</button>
            </div>
            <p className="text-gray-500 text-center py-8">No tasks scheduled for later</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

# Write the files
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, '..', 'frontend', 'generated')

# Write Home.jsx
with open(os.path.join(frontend_dir, 'Home.jsx'), 'w', encoding='utf-8') as f:
    f.write(home_content)
print('✅ Home.jsx written')

# Write Tasks.jsx
with open(os.path.join(frontend_dir, 'Tasks.jsx'), 'w', encoding='utf-8') as f:
    f.write(tasks_content)
print('✅ Tasks.jsx written')

print('✅ Projects.jsx already exists')
print('\n🎉 All components ready!')

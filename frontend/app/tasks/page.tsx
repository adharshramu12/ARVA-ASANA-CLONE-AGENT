'use client';

import TasksUI from "../../generated/Tasks";

export default function TasksPage() {
  return (
    <div className="w-full h-full overflow-auto">
      <TasksUI />
    </div>
  );
}


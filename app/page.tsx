import fs from 'fs';
import path from 'path';
import CodeViewer from '@/components/CodeViewer';

const getFiles = (dir: string, fileList: {name: string, path: string, content: string}[] = [], prefix = '') => {
  try {
    if (!fs.existsSync(dir)) return fileList;
    const files = fs.readdirSync(dir);
    for (const file of files) {
      if (file === 'data') continue; // Skip inner databases
      const fullPath = path.join(dir, file);
      if (fs.statSync(fullPath).isDirectory()) {
         getFiles(fullPath, fileList, `${prefix}${file}/`);
      } else {
         fileList.push({
           name: file,
           path: `${prefix}${file}`,
           content: fs.readFileSync(fullPath, 'utf-8')
         });
      }
    }
  } catch (e) {
    console.error("Error reading directory", e);
  }
  return fileList;
};

export default function Home() {
  const storebotPath = path.join(process.cwd(), 'storebot');
  const files = getFiles(storebotPath);

  return (
    <main className="min-h-screen bg-[#0E1117] text-white">
        <CodeViewer files={files} />
    </main>
  );
}

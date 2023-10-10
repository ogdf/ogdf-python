import {expect, test} from '@jupyterlab/galata';

async function waitIdle(page) {
    await page.waitForTimeout(200);
    const idleLocator = page.locator('#jp-main-statusbar >> text=Idle');
    await idleLocator.waitFor();
    await page.waitForTimeout(200);
}

test.describe.serial('Editor UI Actions', () => {
    test('Run Notebook and capture cell outputs', async ({page}) => {
        // large enough for biggest figure
        // await page.setViewportSize({width: 1000, height: 1000});
        const fileName = "editor-ui.ipynb";
        await page.notebook.createNew(fileName);
        await page.notebook.activate(fileName);
        await page.notebook.openByPath(fileName);
        await page.waitForTimeout(200);

        await page.notebook.setCell(0, "markdown", `
%matplotlib widget

from ogdf_python import *
from ogdf_python.matplotlib import MatplotlibGraphEditor
`);
        await page.notebook.setCellType(0, "code");
        await page.notebook.runCell(0);
        await page.waitForTimeout(200);

        await page.notebook.setCell(1, "markdown", `
G = ogdf.Graph()
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

N1 = G.newNode()
N2 = G.newNode()
N3 = G.newNode()

G.newEdge(N1, N2)
G.newEdge(N1, N3)
e = G.newEdge(N2, N3)

GA.x[N1], GA.y[N1] = 0, 0
GA.x[N2], GA.y[N2] = 100, 0
GA.x[N3], GA.y[N3] = 0, 100
GA.bends[e].emplaceBack(40, 40)

W = MatplotlibGraphEditor(GA)
W
`);
        await page.waitForTimeout(200);
        await page.notebook.setCellType(1, "code");
        await page.notebook.runCell(1);

        await page.notebook.expandCellOutput(1, true);
        await page.waitForTimeout(200);
        const cell = await (await page.notebook.getCell(1)).$(".jp-OutputArea-output");
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-0.png`);

        await page.notebook.setCell(2, "markdown", `
print(W.ax.transData.transform([
    [100, 100], # dbl-click + click
[0, 100], # ctrl-click + drag
[0, 50], # drag-to
[50, 0], # click + del
[0, 0], # click + del
]).tolist())
`);
        await page.waitForTimeout(200);
        await page.notebook.setCellType(2, "code");
        await page.notebook.runCell(2);
        const posText = await page.notebook.getCellTextOutput(2);
        const pos = JSON.parse(posText[0]);
        console.log(pos);
        expect(pos.length).toEqual(5);

        await cell.scrollIntoViewIfNeeded();
        const box = await cell.boundingBox();
        console.log(box);
        await page.mouse.click(box.x + pos[0][0], box.y + box.height - pos[0][1]);
        await page.waitForTimeout(200);

        await page.mouse.dblclick(box.x + pos[0][0], box.y + box.height - pos[0][1]);
        await waitIdle(page);
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-1.png`);

        await page.keyboard.down("Control");
        await page.waitForTimeout(100);
        await page.mouse.dblclick(box.x + pos[1][0], box.y + box.height - pos[1][1]);
        await page.waitForTimeout(100);
        await page.keyboard.up("Control");
        await waitIdle(page);
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-2.png`);

        await page.mouse.move(box.x + pos[1][0], box.y + box.height - pos[1][1]);
        await page.waitForTimeout(100);
        await page.mouse.down();
        await page.waitForTimeout(100);
        await page.mouse.move(box.x + pos[2][0], box.y + box.height - pos[2][1], {steps: 10});
        await page.waitForTimeout(100);
        await page.mouse.up();
        await waitIdle(page);
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-3.png`);

        await page.mouse.click(box.x + pos[3][0], box.y + box.height - pos[3][1]);
        await waitIdle(page);
        await page.keyboard.press("Delete");
        await waitIdle(page);
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-4.png`);

        await page.mouse.click(box.x + pos[4][0], box.y + box.height - pos[4][1]);
        await waitIdle(page);
        await page.keyboard.press("Delete");
        await waitIdle(page);
        expect.soft(await cell.screenshot()).toMatchSnapshot(`editor-ui-5.png`);

        // Save outputs for the next tests
        await page.notebook.save();
    });
});

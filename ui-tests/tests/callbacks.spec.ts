import {expect, galata, test} from '@jupyterlab/galata';
import * as path from 'path';

async function testCallbacks(mode, page) {
    //  0 widget
    //  1 gc disable
    //  2 svg formatter disable
    //  3 import ogdf_python
    //  4 GA create
    //  5 newNode
    //  6 newEdge
    //  7 delEdge
    //  8 delNode
    //  9 clear+new
    // 10 gc run
    await page.notebook.runCellByCell({
        onAfterCellRun: async (idx) => {
            if (idx < 4 || idx == 10) return;
            await page.notebook.expandCellOutput(idx, true);
            await page.waitForTimeout(500);
            for (let c = 4; c <= idx; c++) {
                const cell = await (await page.notebook.getCell(c)).$(".jp-OutputArea-output");
                await cell.scrollIntoViewIfNeeded();
                expect.soft(await cell.screenshot())
                    .toMatchSnapshot(`callbacks-${mode}-run-${idx}-cell-${c}.png`);
            }
        }
    });
    expect((await page.notebook.getCellTextOutput(10))[0]).toEqual("All good!\n")
}

const fileName = 'callbacks.ipynb';

test.use({tmpPath: 'widget-callbacks-test'});

test.describe.serial('Graph change callbacks', () => {
    test.beforeAll(async ({request, tmpPath}) => {
        const contents = galata.newContentsHelper(request);
        await contents.uploadFile(
            path.resolve(__dirname, `./notebooks/${fileName}`),
            `${tmpPath}/${fileName}`
        );
    });

    test.beforeEach(async ({page, tmpPath}) => {
        await page.filebrowser.openDirectory(tmpPath);
        // large enough for biggest figure
        // await page.setViewportSize({width: 500, height: 500});
        await page.notebook.openByPath(`${tmpPath}/${fileName}`);
        await page.notebook.activate(fileName);
        await page.getByText('Edit', {exact: true}).click();
        await page.locator('#jp-mainmenu-edit').getByText('Clear Outputs of All Cells', {exact: true}).click();
    });

    test.afterAll(async ({request, tmpPath}) => {
        const contents = galata.newContentsHelper(request);
        await contents.deleteDirectory(tmpPath);
    });

    test('Works with static inline', async ({page, tmpPath}) => {
        await testCallbacks("static", page);
        await page.notebook.save();
    });

    test('Works with dynamic widget', async ({page, tmpPath}) => {
        await page.notebook.setCell(0, "markdown", "%matplotlib widget");
        await page.notebook.setCellType(0, "code");
        await testCallbacks("widget", page);
        await page.notebook.save();
    });
});

import {expect, galata, test} from '@jupyterlab/galata';
import * as path from 'path';

const fileName = 'sugiyama-simple.ipynb';

test.use({tmpPath: 'widget-modes-test'});

test.describe.serial('Widget Display Modes', () => {
    test.beforeAll(async ({request, tmpPath}) => {
        const contents = galata.newContentsHelper(request);
        await contents.uploadFile(
            path.resolve(__dirname, `./notebooks/${fileName}`),
            `${tmpPath}/${fileName}`
        );
    });

    test.beforeEach(async ({page, tmpPath}) => {
        await page.filebrowser.openDirectory(tmpPath);
    });

    test.afterAll(async ({request, tmpPath}) => {
        const contents = galata.newContentsHelper(request);
        await contents.deleteDirectory(tmpPath);
    });

    test('Run Notebook and capture cell outputs', async ({page, tmpPath}) => {
        // large enough for biggest figure
        await page.setViewportSize({ width: 1000, height: 2000 });
        await page.notebook.openByPath(`${tmpPath}/${fileName}`);
        await page.notebook.activate(fileName);
        await page.getByText('Edit', {exact: true}).click();
        await page.locator('#jp-mainmenu-edit').getByText('Clear Outputs of All Cells', {exact: true}).click();

        await page.notebook.runCellByCell({
            onAfterCellRun: async (idx) => {
                await page.notebook.expandCellOutput(idx, true);
                const cell = await page.notebook.getCellOutput(idx);
                if (cell)
                    expect.soft(await cell.screenshot())
                        .toMatchSnapshot(`notebook-cell-${idx}.png`);
            }
        });
        // Save outputs for the next tests
        await page.notebook.save();
    });
});
